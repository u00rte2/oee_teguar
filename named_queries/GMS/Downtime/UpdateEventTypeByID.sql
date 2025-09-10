UPDATE soc.DowntimeEvents
SET EventCode = :EventCode,
	EventCodeVersion = :EventCodeVersion,
	[Timestamp] = GetDate()
WHERE ID = :ID