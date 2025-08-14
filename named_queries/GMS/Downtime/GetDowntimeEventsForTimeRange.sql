Select
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
            THEN CONCAT(DATEDIFF(second, de.StartTime, CURRENT_TIMESTAMP)/ 3600 % 60, ':',
                        DATEDIFF(second, de.StartTime, CURRENT_TIMESTAMP)/ 60 % 60, ':',
                        DATEDIFF(second, de.StartTime, CURRENT_TIMESTAMP) % 60
                        )
            ELSE CONCAT(DATEDIFF(second, de.StartTime, de.EndTime)/ 3600 % 60, ':',
                        DATEDIFF(second, de.StartTime, de.EndTime)/ 60 % 60, ':',
                        DATEDIFF(second, de.StartTime, de.EndTime) % 60
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
From soc.DowntimeEvents de
Left Join soc.DowntimeCodes dc
On de.EventCode = dc.EventCode
Where LocationName like :LocationName
And ((EndTime > :StartTime and StartTime < :EndTime)
	or
	(EndTime is null and StartTime < :EndTime))
Order By StartTime DESC