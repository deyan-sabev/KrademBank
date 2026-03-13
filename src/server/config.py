import os
from dotenv import load_dotenv

ENV_FILE = os.getenv("ENV_FILE")
if not ENV_FILE:
    ENV_FILE = ".env.bankKDB"

load_dotenv(os.path.join("src", "server", ENV_FILE))

BANK_CODE = os.getenv("BANK_CODE")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

BANK_REGISTER_API = os.getenv("BANK_REGISTER_API")

PORT = int(os.getenv("PORT"))
