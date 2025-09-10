SELECT * FROM
	(SELECT TOP(1)
		'EventCode' AS [SeriesName]
		,dt.EventCode AS [Value]
		,c.[color] AS [Color]
	FROM [soc].[DowntimeEvents] AS dt
	LEFT JOIN [soc].[DowntimeCodes] c
	    ON dt.EventCode = c.EventCode
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
ORDER BY 1