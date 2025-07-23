def get_codes():
	qry = "SELECT * FROM soc.DowntimeCodes ORDER BY ParentEventCode, EventCode"
	pycodes = system.db.runQuery(qry, "glass")
	return pycodes


def get_rows(pyds, parent):
	rows = []
	for row in pyds:
		if row["ParentEventCode"] == parent:
			rows.append(row)
	return rows


def create_tree():
	startCode = 0
	pycodes = get_codes()
	parentCodes = list( set( ( row["ParentEventCode"] for row in pycodes) ) )
	eventPaths = []
	for parentCode in parentCodes:
		eventPaths.append( parentCode )
		children = [ row["EventCode"] for row in pycodes if row["ParentEventCode"] == parentCode ]
		for child in children:
			childRows = get_rows(pycodes, child)
			for row in childRows:
				node = "{parentCode}/"
				eventPaths.append(parentCode)

	for row in pycodes:
		eventPaths.append(parentCode)


	def browseCodes(eventCode):
		pathList = [ ]



		for row in pycodes:
			folderName = row["Name"]
			if row["ParentEventCode"] == eventCode:
				pass
			pathList.append("/{}".format(folderName))
			browseCodes(eventCode)

		children = system.opc.browseServer(OPCServerName,nodeId)
		for child in children:
			elementType = str(child.getElementType())  # SEES FOLDERS AS TYPE OBJECTS INSTEAD OF TYPE "FOLDER"
			childNodeId = str(child.getServerNodeId().getNodeId())  # Get the Node ID ex: n=1;i=x
			folderName = str(child.getDisplayName())  # get the string name of the node in the server
			if elementType == "OBJECT":  # all folders are treated as objects that's why im doing this comparing
				pathList.append(folderName)  # "/"+str(browseServer(childNodeId))
				browseServer(childNodeId)
		return pathList

	PathList = browseServer(codeID)
	for path in PathList:
		print
		path
	return


def create_node_tree():
	# start from the root
	NodeId = ""

	def browseServer(nodeId):
		pathList = [ ]
		children = system.opc.browseServer(OPCServerName,nodeId)
		for child in children:
			elementType = str(child.getElementType())  # SEES FOLDERS AS TYPE OBJECTS INSTEAD OF TYPE "FOLDER"
			childNodeId = str(child.getServerNodeId().getNodeId())  # Get the Node ID ex: n=1;i=x
			folderName = str(child.getDisplayName())  # get the string name of the node in the server
			if elementType == "OBJECT":  # all folders are treated as objects that's why im doing this comparing
				pathList.append(folderName)  # "/"+str(browseServer(childNodeId))
				browseServer(childNodeId)
		return pathList

	PathList = browseServer(NodeId)
	for path in PathList:
		print
		path
	return