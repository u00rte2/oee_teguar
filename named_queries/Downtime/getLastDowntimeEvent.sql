SELECT	de.*,
		dc.ParentEventCode,
		CASE
			WHEN de.EndTime IS NULL
					THEN 'current'
				ELSE 'lastDowntime'
		END AS eventType
FROM soc.DowntimeEvents de
JOIN soc.DowntimeCodes dc
	ON de.EventCode = dc.EventCode
WHERE de.ID IN (	SELECT TOP(15) MAX(ID) AS ID
					FROM soc.DowntimeEvents
					WHERE sourceID = :sourceID
						AND plantID = :plantID
						AND EndTime IS NOT NULL
						AND retired = 0
					GROUP BY sourceID, plantID, lineNumber )
ORDER BY de.lineNumber, de.StartTime DESC