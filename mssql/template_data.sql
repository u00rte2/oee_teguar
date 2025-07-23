/****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP (10000) t.[sourceID]
      ,t.[plantID]
      --,t.[lineLinkID]
	  ,p.lineLinkID
      ,t.[lineNumber]
      ,t.[extruderID]
      ,t.[property]
	  ,p.providerLocal
	  ,p.providerRemote
      ,t.[tagpath]
      ,t.[TableRecordID]
	  ,p.dtrStation
  FROM [Glass].[dbo].[templateData] t
  JOIN soc.plantDef p
	ON t.sourceID = p.sourceID
		AND t.plantID = p.plantID
		AND t.lineNumber = p.lineNumber
		--AND t.lineLinkID = p.lineLinkID
WHERE t.plantID = 4
--and tagpath LIKE '%default%'
