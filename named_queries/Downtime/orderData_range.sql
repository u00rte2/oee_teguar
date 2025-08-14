SELECT
	CASE
		WHEN orderStart > :startDate THEN orderStart
		ELSE :startDate
	END AS t_stamp
	,orderNumber AS EventCode
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
SELECT :endDate AS t_stamp, 0 AS EventCode
ORDER BY t_stamp