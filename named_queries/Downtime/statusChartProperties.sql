SELECT * FROM
	(SELECT TOP(1)
		'EventCode' AS [SeriesName]
		,dt.EventCode AS [Value]
		,c.[color] AS [Color]
	FROM [soc].[DowntimeEvents] AS dt
	LEFT JOIN [soc].[DowntimeCodes] c ON dt.EventCode = c.EventCode
	WHERE sourceID = :sourceID
		AND plantID = :plantID
		AND lineNumber = :lineNumber
	    AND retired = 0
		AND EndTime IS NULL
	ORDER BY 1 DESC) x
UNION
SELECT  DISTINCT
	'EventCode' AS [SeriesName]
	,dt.EventCode AS [Value]
	,c.[color] AS [Color]
FROM [soc].[DowntimeEvents] AS dt
LEFT JOIN [soc].[DowntimeCodes] c ON dt.EventCode = c.EventCode
WHERE sourceID =  :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
    AND retired = 0
	AND EndTime > :startDate
UNION
SELECT DISTINCT 'orderNumber' AS [SeriesName]
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
SELECT 'orderNumber' AS [SeriesName], 0 AS [Value], 'red' AS [Color]
UNION
SELECT 'orderNumber' AS [SeriesName], 123 AS [Value], 'white' AS [Color]
ORDER BY 1,2