import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn: any
cur: any

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_USER_NAME = os.getenv('DB_USER_NAME')
DB_USER_PASSWORD = os.getenv('DB_USER_PASSWORD')

conn = psycopg2.connect(
        host = DB_HOST, port = DB_PORT, dbname = DB_NAME, user = DB_USER_NAME, password = DB_USER_PASSWORD
    )
cur = conn.cursor()

def get_db_cursor():
    return cur

def get_db_connection():
    return conn

def close_connection():
    cur.close()
    conn.close()
