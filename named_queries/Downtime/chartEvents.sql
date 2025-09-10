SELECT
	ca.eventTime AS t_stamp
	,ca.eventName
	,dt.EventCode
	,c.ParentEventCode
	,[WorkOrderUUID] AS orderNumber
	,c.[Name] AS 'seriesName'
	,CASE
		WHEN c.ParentEventCode = 0 THEN 'Running'
		WHEN c.ParentEventCode = 1 THEN 'Generic Downtime'
		WHEN c.ParentEventCode = 2 THEN 'Planned Downtime'
		WHEN c.ParentEventCode = 3 THEN 'Unplanned Downtime'
		ELSE 'Error in parent code'
	END AS 'ParentEventName'
	,c.[color]
FROM [soc].[DowntimeEvents] AS dt
LEFT JOIN [soc].[DowntimeCodes] c
	ON dt.EventCode = c.EventCode
	CROSS APPLY
		(	VALUES 	(CONCAT([name], ': Begin'), StartTime)
					,(CASE
						WHEN EndTime IS NULL
						THEN CONCAT([name], ': Current')
						ELSE CONCAT([name], ': End')
					END
					,CASE
						WHEN EndTime IS NULL
						THEN CURRENT_TIMESTAMP
						ELSE EndTime
					END)
		) AS ca (eventName, eventTime)
WHERE sourceID =  :sourceID
	AND plantID = :plantID
	AND lineNumber = :lineNumber
	AND retired = 0
	AND eventTime > :startDate
ORDER BY 1