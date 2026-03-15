import mysql.connector
from server.config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
