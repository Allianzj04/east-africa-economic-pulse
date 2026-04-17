CREATE TABLE IF NOT EXISTS dim_country (
  id SERIAL PRIMARY KEY,
  code VARCHAR(3) UNIQUE NOT NULL,
  name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_indicator (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE NOT NULL,
  label VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS fact_economic (
  id SERIAL PRIMARY KEY,
  country_id INTEGER REFERENCES dim_country(id),
  indicator_id INTEGER REFERENCES dim_country(id),
  year INTEGER NOT NULL,
  value NUMERIC(15,2),
  UNIQUE(country_id, indicator_id, year)
);

