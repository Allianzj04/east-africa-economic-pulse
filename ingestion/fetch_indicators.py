import wbgapi as wb
import pandas as pd

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
  df_long['year'] = df_long['year'].str.replace('YR', '').astype(int)
  df_long['value'] = df_long['value'].round(2)
  df_long['indicator'] = label
  return df_long


if __name__ == '__main__':
  frames = []
  for code, label in INDICATORS.items():
    df = fetch_indicator(code, label, COUNTRIES)
    frames.append(df)

  data = pd.concat(frames, ignore_index=True)
  # print(data)
  # print(data.shape)
  # print(df)