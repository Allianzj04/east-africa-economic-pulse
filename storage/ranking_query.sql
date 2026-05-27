-- GDP per capita ranking by country in 2023
-- CTE: calculates the rank by GDP per capita in 2023 using RANK()
-- Main query: show the ranking of the 5 nations

WITH ranking AS (
    SELECT 
        c.name AS country_name, 
        ec.year,
		ec.value,
        RANK() OVER (ORDER BY value DESC) AS rank
    FROM fact_economic ec
    JOIN dim_country c ON c.id = ec.country_id
	WHERE year = 2023
)
SELECT 
    country_name, 
    value, 
	rank
FROM ranking;