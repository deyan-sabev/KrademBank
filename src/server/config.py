import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_DIR = os.path.join(BASE_DIR, "env")

print(BASE_DIR, ENV_DIR)

env_name = os.getenv("ENV_FILE")
print(env_name)
if not env_name:
    env_name = ".env.bankKDB"

env_path = os.path.join(ENV_DIR, env_name)

load_dotenv(env_path)

BANK_CODE = os.getenv("BANK_CODE")
BANK_NAME = os.getenv("BANK_NAME")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

BANK_REGISTER_API = os.getenv("BANK_REGISTER_API")
