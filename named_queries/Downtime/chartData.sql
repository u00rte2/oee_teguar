SELECT TOP(1)
	CURRENT_TIMESTAMP AS t_stamp
	,dt.EventCode
FROM [soc].[DowntimeEvents] AS dt
WHERE sourceID = :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
    AND retired = 0
	AND StartTime > :startDate
	AND EndTime IS NULL
UNION
SELECT
	dt.StartTime AS t_stamp
	,dt.EventCode
FROM [soc].[DowntimeEvents] AS dt
WHERE sourceID = :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
    AND retired = 0
	AND StartTime > :startDate
ORDER BY 1