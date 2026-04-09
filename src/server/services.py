import requests
from server.db import get_connection
from server.errors import APIError, is_valid_iban
from server.config import BANK_CODE, BANK_REGISTER_API

def is_my_bank(iban: str):
    return iban[:3] == BANK_CODE

def get_account(cursor, iban: str, for_update=False):
    sql = "SELECT * FROM Accounts WHERE iban=%s"
    if for_update:
        sql += " FOR UPDATE"
    cursor.execute(sql, (iban,))
    return cursor.fetchone()

def _call_bank_register_for_bank(iban: str):
    try:
        url = BANK_REGISTER_API + iban
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        raise APIError(602)

def _call_remote_bank_transactions(bank_api: str, iban: str):
    try:
        url = bank_api + iban
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            try:
                data = r.json()
                if isinstance(data, dict) and data.get("status_code") not in (None, 200): # If the bank returned an error in JSON format
                    raise APIError(data["status_code"], data.get("status_msg"))
                else:
                    raise APIError(651)
            except ValueError:
                raise APIError(651)
        return r.json()
    except requests.RequestException:
        raise APIError(651)
    
def transactions(cursor):
    sql = """
    SELECT
        iban_sender AS IBAN_sender,
        iban_receiver AS IBAN_receiver,
        amount,
        currency,
        reason,
        transaction_datetime AS datetime
    FROM Transactions
    ORDER BY transaction_datetime DESC
    """
    cursor.execute(sql)
    return cursor.fetchall()

def search_transaction(search, cursor):
    if not is_valid_iban(search):
        raise APIError(608)

    if is_my_bank(search):
        account = get_account(cursor, search)
        if not account:
            raise APIError(609)

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
    bank_api = bank_data.get("bank_api")
    if not bank_api:
        raise APIError(701)

    return _call_remote_bank_transactions(bank_api, search)

def process_transaction(data):
    sender = data.get("IBAN_sender")
    receiver = data.get("IBAN_receiver")
    amount = data.get("amount")
    currency = data.get("currency")
    reason = data.get("reason", "")

    if not sender or not receiver or not amount or not currency:
        raise APIError(606)

    if sender == receiver:
        raise APIError(607)

    if not is_valid_iban(sender) or not is_valid_iban(receiver):
        raise APIError(608)

    if currency not in ["EUR", "USD"]:
        raise APIError(605)

    sender_is_mine = is_my_bank(sender)
    receiver_is_mine = is_my_bank(receiver)

    if not sender_is_mine and not receiver_is_mine:
        raise APIError(603)

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:
        db.start_transaction()

        sender_account = get_account(cursor, sender, for_update=sender_is_mine) if sender_is_mine else None
        receiver_account = get_account(cursor, receiver, for_update=receiver_is_mine) if receiver_is_mine else None

        if sender_is_mine and not sender_account:
            db.rollback()
            raise APIError(609)

        if receiver_is_mine and not receiver_account:
            db.rollback()
            raise APIError(652)

        if sender_is_mine and sender_account["balance"] < amount:
            db.rollback()
            raise APIError(601)

        if sender_is_mine and sender_account.get("single_payment_limit") and amount > sender_account["single_payment_limit"]:
            db.rollback()
            raise APIError(604)

        if sender_is_mine and receiver_is_mine:
            cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE iban=%s", (amount, sender))
            cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE iban=%s", (amount, receiver))

        elif sender_is_mine and not receiver_is_mine:
            bank_data = _call_bank_register_for_bank(receiver)
            bank_api = bank_data.get("bank_api")
            if not bank_api:
                db.rollback()
                raise APIError(701)

            try:
                response = requests.post(bank_api, json=data, timeout=10).json()
            except Exception:
                db.rollback()
                raise APIError(651)

            response_code = int(response.get("status_code"))
            if response_code != 1000:
                db.rollback()
                raise APIError(response.get("status_code"), response.get("status_msg"))

            cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE iban=%s", (amount, sender))

        elif not sender_is_mine and receiver_is_mine:
            # Проверка на sender IBAN с банковия регистъра
            bank_data = _call_bank_register_for_bank(sender)
            sender_bank_api = bank_data.get("bank_api")
            if not sender_bank_api:
                db.rollback()
                raise APIError(701)

            try:
                verify = requests.get(sender_bank_api + sender, timeout=10)
                verify_data = verify.json()
            except Exception:
                db.rollback()
                raise APIError(651)

            if isinstance(verify_data, dict) and verify_data.get("status_code") not in (None, 200):
                db.rollback()
                raise APIError(verify_data.get("status_code"), verify_data.get("status_msg"))

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

    except APIError:
        db.rollback()
        raise

    except Exception as e:
        print(e)
        db.rollback()
        raise APIError(651)

    finally:
        cursor.close()
        db.close()
