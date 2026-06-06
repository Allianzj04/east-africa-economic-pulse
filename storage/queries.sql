-- GDP per capita growth rate by country between 2010 and 2023
-- CTE: retrieves the 2010 value using LAG(13) for each country
-- Main query: calculates the growth rate (%) on the 2023 row

WITH growth AS (
    SELECT 
        c.name AS country_name, 
        ec.year,
        LAG(ec.value, 13) OVER (PARTITION BY country_id ORDER BY year) AS pib_2010, 
        ec.value 
    FROM fact_economic ec
    JOIN dim_country c ON c.id = ec.country_id
)
SELECT 
    country_name, 
    pib_2010, 
    value AS pib_2023, 
    ROUND(((value - pib_2010) / pib_2010) * 100) AS growth_rate
FROM growth
WHERE year = 2023;



-- GDP per capita growth rate by country between 2022 and 2023
-- CTE: retrieves the 2022 value using LAG(1) for each country
-- Main query: calculates the growth rate (%) on the 2023 row

WITH year_growth AS (
    SELECT 
        c.name AS country_name, 
        ec.year,
        LAG(ec.value, 1) OVER (PARTITION BY country_id ORDER BY year) AS pib_2022, 
        ec.value 
    FROM fact_economic ec
    JOIN dim_country c ON c.id = ec.country_id
)
SELECT 
    country_name, 
    pib_2022, 
    value AS pib_2023, 
    (value - pib_2022) AS growth,
	ROUND(((value - pib_2022) / pib_2022) * 100) AS growth_rate
FROM year_growth
WHERE year = 2023 ORDER BY growth_rate DESC;