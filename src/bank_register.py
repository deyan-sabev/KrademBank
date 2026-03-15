import sys
from flask import Flask, jsonify
from server.errors import APIError, is_valid_iban

app = Flask(__name__)

banks = {
    "KDB": {
        "bank_name": "KrademBank",
        "bank_api": "http://localhost:5000/KDBbankAPI/transactions/"
    },
    "AAA": {
        "bank_name": "Alpha Bank",
        "bank_api": "http://localhost:5001/AAAbankAPI/transactions/"
    },
    "BBB": {
        "bank_name": "Beta Bank",
        "bank_api": "http://localhost:5002/BBBbankAPI/transactions/"
    }
}

@app.errorhandler(APIError)
def handle_api_error(error: APIError):
    return jsonify({
        "status_code": error.code,
        "status_msg": error.message
    }), error.http_status

@app.route("/bankRegister/bank")
def get_all_banks():
    return jsonify(banks), 200

@app.route("/bankRegister/bank/<iban>")
def get_bank(iban):
    if not is_valid_iban(iban):
        raise APIError(608)

    bank_code = iban[:3]
    if bank_code not in banks:
        raise APIError(701)

    bank = banks[bank_code]
    return jsonify({
        "bank_code": bank_code,
        "bank_name": bank["bank_name"],
        "bank_api": bank["bank_api"]
    }), 200

if __name__ == "__main__":
    port = 5050

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number '{sys.argv[1]}', using default {port}")

    app.run(port=port)
