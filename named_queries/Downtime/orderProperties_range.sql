SELECT DISTINCT 'EventCode' AS [SeriesName]
	,orderNumber AS [Value]
	,IIF((ROW_NUMBER() OVER(ORDER BY orderStart ASC) % 2) = 0, 'green', 'lime') AS [Color]
FROM [soc].[orderTracking]
WHERE sourceID = :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
	AND (
			(orderStart > :startDate AND orderStart < :endDate)
			OR
			(orderEnd > :startDate AND orderEnd < :endDate)
		)
	AND orderNumber > 0
UNION
SELECT 'EventCode' AS [SeriesName], 0 AS [Value], 'red' AS [Color]