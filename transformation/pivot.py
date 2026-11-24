import ingestion.fetch_indicators as f
import polars as pl

def pivot_data(data):
    return data.pivot(on="indicator", index=["country", "year"], values="value").sort(by=["country", "year"])

if __name__ == '__main__':
  frames = []
  for code, label in f.INDICATORS.items():
    df = f.fetch_indicator(code, label, f.COUNTRIES)
    frames.append(df)

  data = pl.concat(frames)
  pivoted_data = pivot_data(data)
  print(pivoted_data)