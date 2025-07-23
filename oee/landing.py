def startup():
	"""
	Determine if HMI or remote use
	If [System]Client/Network/Hostname in table then HMI

	:param event:
	:return:
	"""
	set_cnfsql04_provider()
	pyHostConfig = getHostConfig()
	if pyHostConfig.rowCount == 0:
		system.gui.messageBox("Application will now close.","Host Configuration Not Found!")
		system.util.exit()
	system.tag.writeBlocking( ["[client]user/hostConfig"], [system.dataset.toDataSet(pyHostConfig)] )
	tagpaths = ["[client]user/hostConfig",
				"[System]Client/Network/Hostname",
				"[System]Client/Network/IPAddress",
				"[System]Client/System/ProjectName"]
	hostConfig, clientHost, clientIP, projectName = [obj.value for obj in system.tag.readBlocking(tagpaths)]
	if sessionAlreadyExists(clientHost,clientIP,projectName):
		window = system.nav.openWindow("SessionAlreadyExists")
	elif validUser(pyHostConfig, clientHost):
		window = system.nav.openWindow("Downtime/Downtime_Main")
	else:
		window = system.nav.openWindow("Landing")
	return


def set_cnfsql04_provider():
	glass_provider = oee.util.get_glass_network_provider()
	system.tag.writeBlocking( [ "[client]template/glass_provider" ], [ glass_provider ] )
	return


def get_dev_users():
	devUsers = {
		"blm-008878": { "userName": "Tim" },
		"blm-011237": { "userName": "Tom" },
		"blm-008720": { "userName": "Kevon" },
		"lxt-mt-010000": { "userName": "Zach" },
		"sup-009240": { "userName": "Kevon" }
	}
	return devUsers


def is_developer():
	devUsers = get_dev_users()
	localHostName = system.tag.readBlocking("[System]Client/Network/Hostname")[ 0 ].value
	if localHostName.lower() in devUsers.keys():
		return True
	return False


def visionWindowOpened(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	devUsers = get_dev_users()
	localHostName = system.tag.readBlocking("[System]Client/Network/Hostname")[ 0 ].value
	if localHostName.lower() in devUsers.keys():
		text = "<html><center><b>Welcome {userName}:</b><br>Please select a line to simulate.".format(userName=devUsers[localHostName.lower()]["userName"])
		rc.getComponent("cntUserInfo").getComponent("lbl_notice").text = text
		rc.getComponent("cntSimulateLine").visible = True
		systemName = system.tag.readBlocking("[System]Gateway/SystemName")[ 0 ].value
		if systemName == "Ignition-BLM-SQL02":
			system.tag.writeBlocking([ "[client]user/rights" ],[ "edit" ])
		else:
			system.tag.writeBlocking([ "[client]user/rights" ],[ "view" ])
	else:
		rc.getComponent("cntSimulateLine").visible = False
		system.gui.messageBox("Application will now close.","Unauthorized User!")
		#system.util.exit()
	return


def sessionAlreadyExists(clientHost, clientIP, projectName):
	"""

	:param clientHost:
	:param clientIP:
	:return:
	"""
	sessions = system.dataset.toPyDataSet(system.util.getSessionInfo())
	session_count = len( [ row["address"] for row in sessions
							if row["project"] == projectName
								and ( row["address"] == clientIP
									or row["address"] == clientHost )
								and not row["isDesigner"]] )
	if session_count > 1:
		return True
	return False


def validUser(hostConfig, clientHost):
	for i in range(hostConfig.rowCount):
		if hostConfig.getValueAt(i, "oeeHostname").lower() == clientHost.lower():
			tagpaths = [ "[client]line_info/%s" % colName for colName in hostConfig.columnNames ]
			tagvalues = [ hostConfig[ i ][ colName ] for colName in hostConfig.columnNames ]
			tagpaths.append("[client]user/rights")
			tagvalues.append("edit")
			system.tag.writeBlocking(tagpaths, tagvalues)
			get_provider()
			return True
	return False


def getHostConfig():
	systemName = system.tag.readBlocking("[System]Gateway/SystemName")[ 0 ].value
	if systemName == "Ignition-BLM-SQL02":
		additionalClause = ""
	else:
		additionalClause = "AND gateway = '{}'".format(systemName)
	qry = """
	SELECT 
		[sourceID]
		,[plantID]
		,[lineLinkID]
		,[plantName]
		,[plantCode3]
		,[lineNumber]
		,[providerLocal]
		,[providerRemote]
		,[gateway]
		,[defaultHistorian]
		,[gatewayHostname]
		,[oeeLocation]
		,[oeeHostname]
		,[oeeProjectname]
		,[downtimeEnable]
	FROM [Glass].[soc].[plantDef]
	WHERE [oeeHostname] IS NOT NULL
	{additionalClause} 
	ORDER BY sourceID, plantID, lineNumber
	""".format(additionalClause=additionalClause)
	pyds = system.db.runQuery(qry, "glass")
	return pyds


def updateClientTags(pyds, idx):
	tagpaths = [ "[client]line_info/%s" % colName for colName in pyds.columnNames ]
	tagvalues = [ pyds[idx][colName] for colName in pyds.columnNames ]
	system.tag.writeBlocking(tagpaths, tagvalues)
	get_provider()
	oee.downtime.updateChartData()
	return


def btn_simulate_line(event):
	rc = event.source.parent
	selectedIndex = rc.getComponent('tbl_hostConfig').selectedRow
	ds = rc.getComponent('tbl_hostConfig').data
	py = system.dataset.toPyDataSet(ds)
	updateClientTags(py,selectedIndex)
	window = system.nav.openWindow('Downtime/Downtime_Main')
	return


def tbl_Host_onDoubleClick(self, rowIndex, colIndex, colName, value, event):
	updateClientTags(system.dataset.toPyDataSet( self.data ), rowIndex)
	system.nav.openWindow('Downtime/Downtime_Main')
	return


def get_provider():
	currentGateway = system.tag.readBlocking("[System]Gateway/SystemName")[ 0 ].value
	if currentGateway == "Ignition-BLM-SQL02":
		providerType = "Remote"
		provider = system.tag.readBlocking("[client]line_info/providerRemote")[ 0 ].value
	else:
		providerType = "Local"
		provider = system.tag.readBlocking("[client]line_info/providerLocal")[ 0 ].value
	system.tag.writeBlocking(["[client]user/providerType", "[client]user/provider"], [providerType, provider])
	return


def btn_expand(event):
	window = system.gui.getParentWindow(event)
	size = window.size
	widthMargin = 10
	heightMargin = 25
	sizes = {	"expand": { "x": 0, "y": 0, "width": 800 + widthMargin, "height": 750 + heightMargin },
				"retract": { "x": 0, "y": 0, "width": 420 + widthMargin, "height": 750 + heightMargin }
			}
	if size.width < 500:
		mode = "expand"
	else:
		mode = "retract"
	window.setSize( sizes[mode]["width"], sizes[mode]["height"] )
	return