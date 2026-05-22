import wbgapi as wb
import pandas as pd
import polars as pl

COUNTRIES = ['BDI', 'RWA', 'KEN', 'TZA', 'UGA']
INDICATORS = {
  'NY.GDP.PCAP.CD': 'gdp_per_capita',
}

def fetch_indicator(code, label, countries, start=2010, end=2023):
  df = wb.data.DataFrame(
    code,
    economy=countries,
    time=range(start, end + 1)
  )
  df_long = df.stack().reset_index()
  df_long.columns = ['country', 'year', 'value']
  df_polars = pl.from_pandas(df_long)
  df_polars = df_polars.with_columns(
    pl.col('year').str.replace('YR', '').cast(pl.Int64),
    pl.col('value').round(2),
    pl.lit(label).alias('indicator')
    )
  return df_polars


if __name__ == '__main__':
  frames = []
  for code, label in INDICATORS.items():
    df = fetch_indicator(code, label, COUNTRIES)
    frames.append(df)

  data = pl.concat(frames)
  # print(data)
  print(data.shape)
  # print(df)