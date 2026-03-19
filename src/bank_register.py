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
    try:
        from argparse import ArgumentParser
        parser = ArgumentParser()

        parser.add_argument("--port", type=int, default=5050)
        parser.add_argument("--proxy", action="store_true")

        args = parser.parse_args()

        port = args.port
        use_proxy = args.proxy

        print(f"Running on port {port} | Proxy mode: {use_proxy}")

        if use_proxy:
            from werkzeug.middleware.proxy_fix import ProxyFix
            app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
            app.run(host="0.0.0.0", port=port)
        else:
            app.run(port=port)
    except Exception as e:
        print(e)
