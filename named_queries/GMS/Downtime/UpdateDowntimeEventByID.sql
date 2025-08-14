UPDATE soc.DowntimeEvents
SET CreatedBy = :CreatedBy,
	EventCode = :EventCode,
	EventCodeVersion = :Version,
	[Timestamp] = GetDate(),
	Note = :Note,
    changeoverDetail = :changeoverDetail,
	IsManual = :IsManual
WHERE ID = :ID