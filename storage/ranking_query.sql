-- GDP per capita ranking by country in 2023
-- CTE: calculates the rank by GDP per capita (indicator label = 'gdp_per_capita') in 2023 using RANK()
-- Main query: shows the ranking of countries based on the gdp_per_capita indicator

WITH ranking AS (
    SELECT 
        c.name AS country_name, 
        ec.year,
		ec.value,
        RANK() OVER (ORDER BY value DESC) AS rank
    FROM fact_economic ec
    JOIN dim_country c ON c.id = ec.country_id
	JOIN dim_indicator di ON ec.indicator_id = di.id
	WHERE year = 2023 AND di.label = 'gdp_per_capita'
)
SELECT 
    country_name, 
    value, 
	rank
FROM ranking;