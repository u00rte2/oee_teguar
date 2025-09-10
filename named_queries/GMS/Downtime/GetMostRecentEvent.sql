SELECT TOP (1) DowntimeEvents.*, DowntimeCodes.ParentEventCode
FROM soc.DowntimeEvents
JOIN soc.DowntimeCodes ON DowntimeEvents.EventCode = DowntimeCodes.EventCode
WHERE LocationName = :LocationName
    AND retired = 0
ORDER BY StartTime DESC