import os
from flask import Flask, jsonify, render_template, request
from server.db import get_connection
from server.services import search_transaction, process_transaction
from server.config import PORT, BANK_CODE

template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client", "templates")
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client", "static")
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ---------------------------
# Frontend routes
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html", BANK_CODE=BANK_CODE)

@app.route("/transactions")
def transactions_page():
    return render_template("transactions.html", BANK_CODE=BANK_CODE)

@app.route("/new_transaction")
def new_transaction_page():
    return render_template("new_transaction.html", BANK_CODE=BANK_CODE)

# ---------------------------
# API routes
# ---------------------------
@app.route(f"/{BANK_CODE}bankAPI/transactions/<search>", methods=["GET"])
def get_transactions(search):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    result = search_transaction(search, cursor)
    cursor.close()
    db.close()
    return jsonify(result)

@app.route(f"/{BANK_CODE}bankAPI/transactions/", methods=["POST"])
def create_transaction():
    data = request.json
    result = process_transaction(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=PORT)
