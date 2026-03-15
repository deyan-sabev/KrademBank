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
    port = 5000

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number '{sys.argv[1]}', using default {port}")

    app.run(port=port)
