from flask import Flask, jsonify
from server.errors import error_response

app = Flask(__name__)

banks = {
    "KDB": {
        "bank_name": "KrademBank",
        "bank_api": "http://localhost:5000/KDBbankAPI/transactions/"
    },
    "AAA": {
        "bank_name": "Alpha Bank",
        "bank_api": "http://localhost:5001/bankAPI/transactions/"
    },
    "BBB": {
        "bank_name": "Beta Bank",
        "bank_api": "http://localhost:5002/bankAPI/transactions/"
    }
}

# =========================
# IBAN validation
# =========================
def is_valid_iban(iban):
    if not iban:
        return False
    if len(iban) < 3:
        return False
    if not iban.isalnum():
        return False
    return True

# =========================
# GET all banks
# =========================
@app.route("/bankRegister/banks")
def get_all_banks():
    return jsonify(banks)

# =========================
# GET bank by IBAN
# =========================
@app.route("/bankRegister/bank/<iban>")
def get_bank(iban):
    if not is_valid_iban(iban):
        return jsonify(error_response(701))

    bank_code = iban[:3]

    if bank_code not in banks:
        return jsonify(error_response(701))
    bank = banks[bank_code]

    return jsonify({
        "bank_code": bank_code,
        "bank_name": bank["bank_name"],
        "bank_api": bank["bank_api"]
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)
