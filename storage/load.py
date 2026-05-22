import ingestion.fetch_indicators as f
import psycopg2
from dotenv import load_dotenv
import os
import wbgapi as wb
import polars as pl

load_dotenv()
def get_connection():
  conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
  )
  return conn

info = wb.economy.info()
code_name = {country["id"]: country["value"] for country in info.items}

frames = []
for code, label in f.INDICATORS.items():
  df = f.fetch_indicator(code, label, f.COUNTRIES)
  frames.append(df)

data = pl.concat(frames)
# print(data)

def load_to_db(df):
  conn = get_connection()
  cursor = conn.cursor()
  countries = df['country'].unique()
  for code in countries:
    cursor.execute(
      """
        INSERT INTO dim_country(code, name) VALUES(%s, %s)
        ON CONFLICT DO NOTHING
      """, (code, code_name.get(code))
    )

  for code, label in f.INDICATORS.items():
    cursor.execute(
      """
        INSERT INTO dim_indicator(code, label) values(%s, %s)
        ON CONFLICT DO NOTHING
      """, (code, label)
    )

  for row in df.iter_rows(named=True):
    cursor.execute(
      """
        SELECT id FROM dim_country WHERE dim_country.code=%s
      """, (row["country"],)
    )
    country_id = cursor.fetchone()[0]
    cursor.execute(
      """
        SELECT id FROM dim_indicator WHERE dim_indicator.label=%s
      """, (row["indicator"],)
    )
    indicator_id = cursor.fetchone()[0]
    cursor.execute(
      """
        INSERT INTO fact_economic(country_id, indicator_id, year, value) values(%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
      """, (country_id, indicator_id, row["year"], row["value"])
    )
    
  conn.commit()
  cursor.close()
  conn.close()

if __name__ == '__main__':
    load_to_db(data)