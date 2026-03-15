from flask import Flask, jsonify, render_template, request
from os import path
from server.db import get_connection
from server.services import search_transaction, process_transaction
from server.config import PORT, BANK_CODE

template_path = path.join(path.dirname(path.abspath(__file__)), "client", "templates")
static_path = path.join(path.dirname(path.abspath(__file__)), "client", "static")
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ----------------------------------------------------
# Frontend routes (HTML страници)
# ----------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", active="home", BANK_CODE=BANK_CODE)

@app.route("/transactions")
def transactions_page():
    return render_template("transactions.html", active="transactions", BANK_CODE=BANK_CODE)

@app.route("/new_transaction")
def new_transaction_page():
    return render_template("new_transaction.html", active="new_transaction", BANK_CODE=BANK_CODE)

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
    return jsonify(result)

@app.route(f"/{BANK_CODE}bankAPI/transactions/", methods=["POST"])
def create_transaction():
    data = request.json
    result = process_transaction(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=PORT)
