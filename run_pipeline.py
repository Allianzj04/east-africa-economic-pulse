import ingestion.fetch_indicators as f
import storage.load as l
import polars as pl
from dotenv import load_dotenv
from prefect import task, flow

load_dotenv()

@task
def ingestion():
  frames = []
  for code, label in f.INDICATORS.items():
    df = f.fetch_indicator(code, label, f.COUNTRIES)
    frames.append(df)

  data = pl.concat(frames)
  return data

@task
def storage(data):
  l.load_to_db(data)

@flow
def launch():
  data = ingestion()
  storage(data)


if __name__ == '__main__':
  launch()