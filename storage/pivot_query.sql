SELECT 
	c.name as country, 
	ec.year, 
	MAX(CASE WHEN i.label = 'gdp_per_capita' THEN ec.value END) as gdp,
	MAX(CASE WHEN i.label = 'inflation' 	 THEN ec.value END) as inflation,
	MAX(CASE WHEN i.label = 'exchange_rate'  THEN ec.value END) as exchange_rate,
	MAX(CASE WHEN i.label = 'unemployment'   THEN ec.value END) as unemployment
FROM fact_economic as ec
JOIN dim_country c ON ec.country_id = c.id
JOIN dim_indicator i ON ec.indicator_id = i.id
GROUP BY c.name, ec.year
ORDER BY c.name, ec.year;