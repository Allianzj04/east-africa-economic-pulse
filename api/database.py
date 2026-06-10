import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
  config = {
      "dbname": os.getenv("DB_NAME"),
      "user": os.getenv("DB_USER"),
      "password": os.getenv("DB_PASSWORD"),
      "host": os.getenv("DB_HOST"),
      "port": os.getenv("DB_PORT")
  }
  conn = psycopg2.connect(**config)
  return conn

def execute_query(sql, params=None):
  conn = None
  cursor = None
  try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    columns = [col.name for col in cursor.description]
    results = [dict(zip(columns, row)) for row in rows]
    return results
  finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
