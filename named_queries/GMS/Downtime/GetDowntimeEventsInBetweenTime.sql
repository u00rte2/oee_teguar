SELECT *
FROM soc.DowntimeEvents
WHERE LocationName LIKE :LocationName
    AND retired = 0
    AND ((EndTime > :StartTime AND StartTime < :EndTime)
	OR
	(EndTime IS NULL AND StartTime < :EndTime))
ORDER BY StartTime ASC