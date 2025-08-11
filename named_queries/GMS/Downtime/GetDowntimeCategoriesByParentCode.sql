SELECT DISTINCT Category FROM soc.DowntimeCodes
WHERE ParentEventCode = :ParentEventCode AND Category != 'Changeover'
AND IsActive = 1