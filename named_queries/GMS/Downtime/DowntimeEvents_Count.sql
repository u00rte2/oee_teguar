SELECT COUNT(*) AS eventCount
FROM soc.DowntimeEvents
WHERE lineNumber = :lineNumber
    AND EventCode = 1
    AND [Timestamp] > :StartTime
    AND retired = 0
ORDER BY 1 DESC