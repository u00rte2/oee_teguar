UPDATE soc.DowntimeEvents
SET EndTime = :EndTime,
	OriginalEndTime = :EndTime,
	[Timestamp] = GetDate()
WHERE LocationName = :LocationName
	AND EndTime IS NULL