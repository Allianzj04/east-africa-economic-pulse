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