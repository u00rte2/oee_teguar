Select *
From soc.DowntimeEvents
Where LocationName like :LocationName
And ((EndTime > :StartTime and StartTime < :EndTime)
	or
	(EndTime is null and StartTime < :EndTime))
Order By StartTime ASC