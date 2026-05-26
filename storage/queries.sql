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