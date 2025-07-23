# Params needed for the following functions
# plantID = event.source.parent.plantID
# cnfsql04Name = event.source.parent.cnfsql04Name
# lineNumber = event.source.parent.lineNumber


def getMainData(event):  # Returns all line data for plant
	cnfsql04TagPath = cnfsql04Name + 'OT/Blender Data/blenderData'  # Path where main data is stored
	ds = system.tag.readBlocking(cnfsql04TagPath)[ 0 ].value
	rowsToDelete = [ ]
	for idx in range(ds.getRowCount()):
		if ds.getValueAt(idx,'plantID') != plantID:
			rowsToDelete.append(idx)
	rawData = system.dataset.deleteRows(ds,rowsToDelete)
	event.source.parent.rawData = rawData
	return


def getLineData(event):  # Returns all line data for plant
	ds = rawData  # This is the dataset from the previous function
	rowsToDelete = [ ]
	for idx in range(ds.getRowCount()):
		if ds.getValueAt(idx,'lineNumber') != lineNumber:
			rowsToDelete.append(idx)
	headerData = system.dataset.deleteRows(ds,rowsToDelete)
	event.source.parent.headerData = headerData
	return


def getDeltaData(event):  # Returns all line delta data for plant
	deltaTagPath = cnfsql04Name + 'OT/Blender Data/PlantExhaustDelta'  # Path where main data is stored
	dsDelta = system.tag.readBlocking(deltaTagPath)[ 0 ].value
	# Set rawdata
	rowsToDeleteDelta = [ ]
	for idx in range(dsDelta.getRowCount()):
		if dsDelta.getValueAt(idx,'plantID') != plantID:
			rowsToDeleteDelta.append(idx)
	dsDeltaRaw = system.dataset.deleteRows(dsDelta,rowsToDeleteDelta)
	event.source.parent.deltaPercentData = dsDeltaRaw
	return


def getActionItems(event):  # Returns all line action items data for plant
	actionItem = cnfsql04Name + 'OT/Glass/dsSocActionItems'  # Path where main data is stored
	dsActionItem = system.tag.readBlocking(actionItem)[ 0 ].value
	# Set rawdata
	rowsToDeleteActionItem = [ ]
	for idx in range(dsActionItem.getRowCount()):
		if dsActionItem.getValueAt(idx,'plantID') != plantID:
			rowsToDeleteActionItem.append(idx)
	dsActionItemRaw = system.dataset.deleteRows(dsActionItem,rowsToDeleteActionItem)
	event.source.parent.actionItems = dsActionItemRaw
	return
