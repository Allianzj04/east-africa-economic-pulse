import ingestion.fetch_indicators as f
import polars as pl

from api.database import execute_query

def load_wide_from_db():
    wide = execute_query(
      """
        SELECT 
          c.name as country, 
          ec.year, 
          MAX(CASE WHEN i.label = 'gdp_per_capita' THEN ec.value END) as gdp_per_capita,
          MAX(CASE WHEN i.label = 'inflation' 	 THEN ec.value END) as inflation,
          MAX(CASE WHEN i.label = 'exchange_rate'  THEN ec.value END) as exchange_rate,
          MAX(CASE WHEN i.label = 'unemployment'   THEN ec.value END) as unemployment
        FROM fact_economic as ec
        JOIN dim_country c ON ec.country_id = c.id
        JOIN dim_indicator i ON ec.indicator_id = i.id
        GROUP BY c.name, ec.year
        ORDER BY c.name, ec.year;
      """
    )
    return pl.DataFrame(wide)
"""
def pivot_data(data):
    return (
        data
        .pivot(on="indicator", index=["country", "year"], values="value")
        .sort(by=["country", "year"])
    )

def build_pivoted_data():
    frames = []
    for code, label in f.INDICATORS.items():
        df = f.fetch_indicator(code, label, f.COUNTRIES)
        frames.append(df)
    data = pl.concat(frames)
    return pivot_data(data)
    """

if __name__ == '__main__':
    # pivoted_data = build_pivoted_data()
    # print(pivoted_data)
    wide_data = load_wide_from_db()
    print(wide_data.shape)