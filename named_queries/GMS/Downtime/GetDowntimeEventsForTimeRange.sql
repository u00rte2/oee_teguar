SELECT
	de.ID,
	de.LocationName,
	(SELECT [Name] FROM [soc].[DowntimeCodes] WHERE [EventCode] = dc.[ParentEventCode]) AS ParentEventName,
	dc.[Category],
	de.EventCode,
	de.OriginalEventCode,
	(SELECT [Name] FROM [soc].[DowntimeCodes] WHERE [EventCode] = de.OriginalEventCode) AS OriginalEventName,
	dc.ParentEventCode,
	de.EventCodeVersion,
	de.OriginalEventCodeVersion,
	dc.[Name],
	dc.[Description],
	dc.IsDowntime,
	dc.IsPlanned,
	de.IsManual,
	de.IsChangeoverDowntime,
	dc.OperatorOverride,
	dc.OperatorSelectable,
	dc.RequireOverride,
	dc.RequireNote,
	de.CreatedBy,
	de.OriginalCreatedBy,
	de.StartTime,
	de.OriginalStartTime,
	de.EndTime,
	CASE
		WHEN de.EndTime IS NULL
            THEN CONCAT(DATEDIFF(SECOND, de.StartTime, CURRENT_TIMESTAMP)/ 3600, ':',
                        DATEDIFF(SECOND, de.StartTime, CURRENT_TIMESTAMP)/ 60 % 60, ':',
                        DATEDIFF(SECOND, de.StartTime, CURRENT_TIMESTAMP) % 60
                        )
            ELSE CONCAT(DATEDIFF(SECOND, de.StartTime, de.EndTime)/ 3600, ':',
                        DATEDIFF(SECOND, de.StartTime, de.EndTime)/ 60 % 60, ':',
                        DATEDIFF(SECOND, de.StartTime, de.EndTime) % 60
                        )
    END AS Duration,
	de.OriginalEndTime,
	de.WorkOrderUUID,
	de.RunUUID,
	de.Shift,
	de.Note,
	de.changeoverDetail,
	de.[Timestamp],
	de.[t_stamp]
FROM soc.DowntimeEvents de
LEFT JOIN soc.DowntimeCodes dc
ON de.EventCode = dc.EventCode
WHERE de.LocationName LIKE :LocationName
        AND de.retired = 0
        AND ((de.EndTime > :StartTime AND de.StartTime < :EndTime)
	    OR (de.EndTime IS NULL AND de.StartTime < :EndTime))
ORDER BY de.StartTime DESC