SELECT TOP (1) DowntimeEvents.*, DowntimeCodes.ParentEventCode
FROM soc.DowntimeEvents
JOIN soc.DowntimeCodes ON DowntimeEvents.EventCode = DowntimeCodes.EventCode
WHERE LocationName = :LocationName
ORDER BY StartTime DESC