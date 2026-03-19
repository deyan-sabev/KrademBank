import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, render_template, request
from server.errors import APIError
from server.db import get_connection
from server.services import search_transaction, process_transaction
from server.config import BANK_CODE, BANK_NAME

template_path = os.path.join(BASE_DIR, "client", "templates")
static_path = os.path.join(BASE_DIR, "client", "static")

app = Flask(__name__, template_folder=template_path, static_folder=static_path)

@app.errorhandler(APIError)
def handle_api_error(error: APIError):
    return jsonify({
        "status_code": error.code,
        "status_msg": error.message
    }), error.http_status

# ----------------------------------------------------
# Frontend routes (HTML страници)
# ----------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", active="home", BANK_CODE=BANK_CODE, BANK_NAME=BANK_NAME)

@app.route("/transactions")
def transactions_page():
    return render_template("transactions.html", active="transactions", BANK_CODE=BANK_CODE, BANK_NAME=BANK_NAME)

@app.route("/new_transaction")
def new_transaction_page():
    return render_template("new_transaction.html", active="new_transaction", BANK_CODE=BANK_CODE, BANK_NAME=BANK_NAME)

# ----------------------------------------------------
# API routes
# ----------------------------------------------------
@app.route(f"/{BANK_CODE}bankAPI/transactions/<search>", methods=["GET"])
def get_transactions(search):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    result = search_transaction(search, cursor)
    cursor.close()
    db.close()
    return jsonify(result), 200

@app.route(f"/{BANK_CODE}bankAPI/transactions/", methods=["POST"])
def create_transaction():
    data = request.json
    result = process_transaction(data)
    return jsonify(result), 200

if __name__ == "__main__":
    try:
        from argparse import ArgumentParser
        parser = ArgumentParser()

        parser.add_argument("--port", type=int, default=5000)
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
