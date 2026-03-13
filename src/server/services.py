import requests
from .db import get_connection
from .errors import error_response
from .config import BANK_CODE, BANK_REGISTER_API

def is_valid_iban(iban: str):
    if not iban:
        return False
    if len(iban) > 22:
        return False
    if not iban.isalnum():
        return False
    return True

def is_my_bank(iban: str):
    return iban[:3] == BANK_CODE

def _call_bank_register_for_bank(iban: str):
    try:
        url = BANK_REGISTER_API + iban
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return error_response(602)

def _call_remote_bank_transactions(bank_api: str, iban: str):
    try:
        url = bank_api + iban
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            try:
                return r.json()
            except ValueError:
                return error_response(651)
        return r.json()
    except requests.RequestException:
        return error_response(651)

def search_transaction(search, cursor):
    if not is_valid_iban(search):
        return error_response(608)
    
    if is_my_bank(search):
        sql = """
        SELECT
            iban_sender AS IBAN_sender,
            iban_receiver AS IBAN_receiver,
            amount,
            currency,
            reason,
            transaction_datetime AS datetime
        FROM Transactions
        WHERE iban_sender=%s OR iban_receiver=%s
        """
        cursor.execute(sql, (search, search))
        return cursor.fetchall()
    
    bank_data = _call_bank_register_for_bank(search)
    if isinstance(bank_data, dict) and bank_data.get("status_code") not in (None, 200): # if bank register returned an error_response, forward it
        return bank_data
    
    bank_api = bank_data.get("bank_api")
    
    if not bank_api:
        return error_response(701)
    
    return _call_remote_bank_transactions(bank_api, search)

def process_transaction(data):
    sender = data.get("IBAN_sender")
    receiver = data.get("IBAN_receiver")
    amount: float = data.get("amount")
    currency = data.get("currency")
    reason = data.get("reason", "")

    if not sender or not receiver or not amount or not currency:
        return error_response(606)

    if sender == receiver:
        return error_response(607)

    if not is_valid_iban(sender) or not is_valid_iban(receiver):
        return error_response(608)

    if currency not in ["EUR", "USD"]:
        return error_response(605)

    sender_is_mine = is_my_bank(sender)
    receiver_is_mine = is_my_bank(receiver)

    if not sender_is_mine and not receiver_is_mine:
        return error_response(603)

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:
        db.start_transaction()
        if sender_is_mine and receiver_is_mine:
            cursor.execute(
                """
                SELECT balance, single_payment_limit, currency
                FROM Accounts
                WHERE iban=%s
                FOR UPDATE
                """,
                (sender,)
            )
            sender_account = cursor.fetchone()
            if not sender_account:
                db.rollback()
                return error_response(608)
            if sender_account["balance"] < amount:
                db.rollback()
                return error_response(601)
            limit = sender_account["single_payment_limit"]
            if limit and amount > limit:
                db.rollback()
                return error_response(604)

            cursor.execute("SELECT iban FROM Accounts WHERE iban=%s FOR UPDATE", (receiver,))
            if not cursor.fetchone():
                db.rollback()
                return error_response(652)

            cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE iban=%s", (amount, sender))
            cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE iban=%s", (amount, receiver))

        elif sender_is_mine and not receiver_is_mine:
            cursor.execute(
                """
                SELECT balance, single_payment_limit
                FROM Accounts
                WHERE iban=%s
                FOR UPDATE
                """,
                (sender,)
            )
            sender_account = cursor.fetchone()
            if not sender_account:
                db.rollback()
                return error_response(608)
            if sender_account["balance"] < amount:
                db.rollback()
                return error_response(601)

            bank_data = _call_bank_register_for_bank(receiver)
            if "bank_api" not in bank_data:
                db.rollback()
                return bank_data
            
            bank_api = bank_data["bank_api"]

            try:
                request = requests.post(bank_api, json=data, timeout=10)
                response = request.json()
            except:
                db.rollback()
                return error_response(651)

            if response["status_code"] != 200:
                db.rollback()
                return response

            cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE iban=%s", (amount, sender))

        elif not sender_is_mine and receiver_is_mine:
            bank_data = _call_bank_register_for_bank(sender)
            if "bank_api" not in bank_data:
                db.rollback()
                return bank_data

            sender_bank_api = bank_data["bank_api"]

            try:
                verify = requests.get(sender_bank_api + sender, timeout=5)
                verify_data = verify.json()
            except:
                db.rollback()
                return error_response(651)

            if isinstance(verify_data, dict) and verify_data.get("status_code") not in (None, 200):
                db.rollback()
                return verify_data

            cursor.execute("SELECT iban FROM Accounts WHERE iban=%s FOR UPDATE", (receiver,))

            if not cursor.fetchone():
                db.rollback()
                return error_response(652)
            
            cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE iban=%s", (amount, receiver))

        cursor.execute(
            """
            INSERT INTO Transactions
            (iban_sender, iban_receiver, amount, currency, reason)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (sender, receiver, amount, currency, reason)
        )
        db.commit()
        return {"status_code": 200, "status_msg": "Успешна транзакция."}

    except Exception:
        db.rollback()
        return error_response(651)

    finally:
        cursor.close()
        db.close()
