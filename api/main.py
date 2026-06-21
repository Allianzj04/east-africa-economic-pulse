from api.database import execute_query
from fastapi import FastAPI

app = FastAPI()

@app.get("/countries")
def country_list():
  return execute_query(
    """
      SELECT code, name FROM dim_country;
    """
  )

@app.get("/gdp")
def country_gdp(
  page: int = 1,
  limit: int = 20):
  OFFSET = (page - 1) * limit
  return execute_query(
    """
      SELECT c.name AS country, ec.year, ec.value
      FROM dim_country c
      JOIN fact_economic ec ON c.id = ec.country_id
      LIMIT %s OFFSET ap%s;
    """, (limit, OFFSET)
  )