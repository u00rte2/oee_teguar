SELECT TOP (1) EventCode
FROM soc.DowntimeEvents
WHERE LocationName = :LocationName
    AND retired = 0
ORDER BY StartTime DESC