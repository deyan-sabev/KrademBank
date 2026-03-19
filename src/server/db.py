import mysql.connector
from server.config import DB_CONFIG

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print("Грешка при опит за свързване с БД:", e)
        raise
