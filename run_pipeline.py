import ingestion.fetch_indicators as f
import storage.load as l
import pandas as pd
from dotenv import load_dotenv
from prefect import task, flow

@task
def ingestion():
  frames = []
  for code, label in f.INDICATORS.items():
    df = f.fetch_indicator(code, label, f.COUNTRIES)
    frames.append(df)

  data = pd.concat(frames, ignore_index=True)
  return data

@task
def storage(data):
  load_dotenv()
  l.load_to_db(data)

@flow
def launch():
  data = ingestion()
  storage(data)


if __name__ == '__main__':
  launch()