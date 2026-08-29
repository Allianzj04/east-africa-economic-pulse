from api.database import execute_query
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="dashboard"), name="static")

@app.get("/")
def root():
    return FileResponse("dashboard/index.html")

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
      LIMIT %s OFFSET %s;
    """, (limit, OFFSET)
  )

@app.get("/gdp/{country_code}")
def country_code_gdp(country_code: str):
  return execute_query(
    """
      SELECT c.name AS country, ec.year, ec.value
      FROM dim_country c
      JOIN fact_economic ec ON c.id = ec.country_id
      WHERE c.code = %s;
    """, (country_code,)
  )
@app.get("/countries/ranking")
def country_ranking(
  year: int = 2023):
  return execute_query(
    """
WITH ranking AS (
    SELECT 
        c.name AS country_name, 
        ec.year,
		ec.value,
        RANK() OVER (ORDER BY value DESC) AS rank
    FROM fact_economic ec
    JOIN dim_country c ON c.id = ec.country_id
	WHERE year = %s
)
SELECT 
    country_name, 
    value, 
	rank
FROM ranking;
    """, (year, )
  )