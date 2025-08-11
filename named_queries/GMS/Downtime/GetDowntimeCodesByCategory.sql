SELECT
	[EventCode]
	,[Name]
	,[Description]
	,[IsDowntime]
	,[IsPlanned]
	,[OperatorOverride]
	,[OperatorSelectable]
	,[RequireOverride]
	,[RequireNote]
	,[Version]
	,[CreatedBy]
	,[Timestamp]
	,[Category]
	,[IsActive]
	,[color]
	,[ID]
	,[ParentEventCode]
FROM soc.DowntimeCodes
WHERE Category = :Category
AND IsActive = 1