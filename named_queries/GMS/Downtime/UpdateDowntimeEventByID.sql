UPDATE soc.DowntimeEvents
SET CreatedBy = :CreatedBy,
	EventCode = :EventCode,
	EventCodeVersion = :Version,
	[Timestamp] = GetDate(),
	Note = :Note,
	IsManual = :IsManual
WHERE ID = :ID