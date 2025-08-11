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
WHERE de.ID =  :eventID
ORDER BY de.lineNumber, de.StartTime DESC