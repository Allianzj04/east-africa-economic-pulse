import psycopg2
import os
from dotenv import load_dotenv
import urllib.parse

def get_connection():
  load_dotenv()
  database_url = os.getenv('DATABASE_URL')
  parsed = urllib.parse.urlparse(database_url)
  conn = psycopg2.connect(
    dbname=parsed.path[1:],
    host=parsed.hostname,
    user=parsed.username,
    password=parsed.password,
    port=parsed.port,
  )
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
