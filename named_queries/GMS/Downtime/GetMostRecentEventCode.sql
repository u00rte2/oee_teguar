SELECT TOP (1) EventCode
FROM soc.DowntimeEvents
WHERE LocationName = :LocationName
ORDER BY StartTime DESC