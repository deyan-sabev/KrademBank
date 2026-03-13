import requests
from datetime import datetime
from .db import get_connection
from .errors import error_response
from .config import BANK_CODE, BANK_REGISTER_API

def is_valid_iban(iban):
    if not iban:
        return False
    if len(iban) > 22:
        return False
    if not iban.isalnum():
        return False
    return True

def is_my_bank(iban):
    return iban[:3] == BANK_CODE

def search_transaction(search, cursor):
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

def process_transaction(data):
    sender = data.get("IBAN_sender")
    receiver = data.get("IBAN_receiver")
    amount = data.get("amount")
    currency = data.get("currency")
    reason = data.get("reason", "")

    if not sender or not receiver or not amount or not currency:
        return error_response(603)

    if sender == receiver:
        return error_response(603)

    if not is_valid_iban(sender) or not is_valid_iban(receiver):
        return error_response(603)

    if currency not in ["EUR", "USD"]:
        return error_response(603)

    if not is_my_bank(sender):
        return error_response(603)

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:
        db.start_transaction()
        cursor.execute("""
            SELECT balance, single_payment_limit, currency
            FROM Accounts
            WHERE iban=%s
            FOR UPDATE
        """, (sender,))
        sender_account = cursor.fetchone()

        if not sender_account:
            db.rollback()
            return error_response(603)

        if sender_account["currency"] != currency:
            db.rollback()
            return error_response(603)

        if sender_account["balance"] < amount:
            db.rollback()
            return error_response(601)

        limit = sender_account["single_payment_limit"]
        if limit and amount > limit:
            db.rollback()
            return error_response(604)

        if is_my_bank(receiver):
            cursor.execute("""
                SELECT iban FROM Accounts WHERE iban IN (%s,%s) FOR UPDATE
            """, (sender, receiver))
            accounts = cursor.fetchall()
            if len(accounts) < 2:
                db.rollback()
                return error_response(652)

            cursor.execute(
                "UPDATE Accounts SET balance = balance - %s WHERE iban=%s",
                (amount, sender)
            )
            cursor.execute(
                "UPDATE Accounts SET balance = balance + %s WHERE iban=%s",
                (amount, receiver)
            )

        else:
            try:
                r = requests.get(BANK_REGISTER_API + receiver, timeout=3)
                bank_data = r.json()
            except:
                db.rollback()
                return error_response(602)

            if "bank_api" not in bank_data:
                db.rollback()
                return bank_data

            bank_api = bank_data["bank_api"]

            try:
                resp = requests.post(bank_api, json=data, timeout=3)
                resp_json = resp.json()
            except:
                db.rollback()
                return error_response(651)

            if resp_json["status_code"] != 200:
                db.rollback()
                return resp_json

            cursor.execute(
                "UPDATE Accounts SET balance = balance - %s WHERE iban=%s",
                (amount, sender)
            )

        cursor.execute("""
            INSERT INTO Transactions
            (iban_sender, iban_receiver, amount, currency, reason, transaction_datetime)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (sender, receiver, amount, currency, reason, datetime.now()))
        db.commit()

        return {"status_code": 200, "status_msg": "Success"}

    except Exception:
        db.rollback()
        return error_response(651)

    finally:
        cursor.close()
        db.close()
