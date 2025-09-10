SELECT TOP(1)
	CURRENT_TIMESTAMP AS t_stamp
	,dt.EventCode
	,NULL AS orderNumber
FROM [soc].[DowntimeEvents] AS dt
WHERE sourceID = :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
	AND StartTime > :startDate
	AND EndTime IS NULL
UNION
SELECT
	dt.StartTime AS t_stamp
	,dt.EventCode
	,NULL AS orderNumber
FROM [soc].[DowntimeEvents] AS dt
WHERE sourceID = :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
    AND retired = 0
	AND StartTime > :startDate
UNION
/*  orderData_range  */
SELECT
	CASE
		WHEN orderStart > :startDate THEN orderStart
		ELSE :startDate
	END AS t_stamp
	,NULL AS EventCode
	,orderNumber
FROM [soc].[orderTracking]
WHERE sourceID = :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
	AND (
		(orderStart > :startDate AND orderStart < :endDate)
		OR
		(orderEnd > :startDate AND orderEnd < :endDate)
	)
UNION
SELECT CURRENT_TIMESTAMP AS t_stamp, NULL AS EventCode, 123 AS orderNumber
ORDER BY 1