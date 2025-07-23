/* All Events */
SELECT TOP (1000)
	de.lineNumber,
	de.WorkOrderUUID AS orderNumber,
	de.[EventCode],
	dc.Category,
	dc.[Name],
	dc.[Description],
	de.Note,
	de.StartTime,
	de.EndTime,
	de.[Timestamp],
	de.[t_stamp],
	de.[retired],
	de.[CreatedBy],
	de.[OriginalCreatedBy],
	de.[lastActor],
	de.[LocationName],
	de.[OriginalEventCode],
	de.[EventCodeVersion],
	de.[OriginalEventCodeVersion],
	de.[OriginalStartTime],
	de.[OriginalEndTime],
	de.[RunUUID],
	de.[Shift],
	de.[Note],
	de.[IsManual],
	de.[IsChangeoverDowntime],
	de.[sourceID],
	de.[plantID],
	de.[lineLinkID]
FROM [Glass].[soc].[DowntimeEvents] de
JOIN  soc.DowntimeCodes dc
	ON de.EventCode = dc.EventCode
ORDER BY de.ID DESC

/* Current and Last Downtime Events */
EXEC	[soc].[getDowntimeEvents_SP] @sourceID = N'1', @plantID = N'1'

/* Current Event */
SELECT	ID,
			EventCode,
			IsManual,
			StartTime,
			EndTime,
			CASE
				WHEN EndTime IS NULL
						THEN 'current'
					ELSE 'lastDowntime'
			END AS eventType,
			sourceID,
			plantID,
			lineLinkID,
			lineNumber
	FROM soc.DowntimeEvents
	WHERE (sourceID = 1 AND plantID = 1 AND EndTime IS NULL AND retired=0)
	ORDER BY lineNumber, StartTime DESC



--/* Last Closed Downtime Event */
--SELECT	ID,
--			EventCode,
--			IsManual,
--			StartTime,
--			EndTime,
--			CASE
--				WHEN EndTime IS NULL
--						THEN 'current'
--					ELSE 'lastDowntime'
--			END AS eventType,
--			sourceID,
--			plantID,
--			lineLinkID,
--			lineNumber
--	FROM soc.DowntimeEvents
--	WHERE ID IN (	SELECT TOP(15) MAX(ID) AS ID FROM soc.DowntimeEvents
--						WHERE sourceID = 1
--							AND plantID = 1
--							AND EndTime IS NOT NULL
--							AND retired=0
--							AND EventCode != 0
--						GROUP BY sourceID, plantID, lineNumber )
--	ORDER BY lineNumber, StartTime DESC


--/* Most Recent Downtime Event */
--SELECT	ID,
--			EventCode,
--			IsManual,
--			StartTime,
--			EndTime,
--			'Most Recent Downtime Event' AS eventType,
--			sourceID,
--			plantID,
--			lineLinkID,
--			lineNumber
--	FROM soc.DowntimeEvents
--	WHERE ID IN (	SELECT TOP(15) MAX(ID) AS ID FROM soc.DowntimeEvents
--						WHERE sourceID = 1
--							AND plantID = 1
--							AND retired=0
--							AND EventCode != 0
--						GROUP BY sourceID, plantID, lineNumber )
--	ORDER BY lineNumber, StartTime DESC



