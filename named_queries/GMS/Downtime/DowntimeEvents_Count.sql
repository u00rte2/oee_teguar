SELECT COUNT(*) AS eventCount
FROM soc.DowntimeEvents
WHERE lineNumber = :lineNumber AND EventCode = 1 AND [Timestamp] > :StartTime
ORDER BY 1 DESC