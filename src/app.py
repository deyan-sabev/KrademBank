import os
from flask import Flask, jsonify, render_template, request
from server.services import search_transaction, process_transaction
from server.config import PORT

template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client", "templates")
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client", "static")
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ---------------------------
# Frontend routes
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transactions")
def transactions_page():
    return render_template("transactions.html")

@app.route("/new_transaction")
def new_transaction_page():
    return render_template("new_transaction.html")

# ---------------------------
# API routes
# ---------------------------
@app.route("/KDBbankAPI/transactions/<search>", methods=["GET"])
def get_transactions(search):
    from server.db import get_connection
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    result = search_transaction(search, cursor)
    cursor.close()
    db.close()
    return jsonify(result)

@app.route("/KDBbankAPI/transactions/", methods=["POST"])
def create_transaction():
    data = request.json
    result = process_transaction(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
