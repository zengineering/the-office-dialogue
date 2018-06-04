SELECT speaker, count(*) as frequency FROM office_quotes GROUP BY speaker ORDER BY count(*) DESC LIMIT 30;
