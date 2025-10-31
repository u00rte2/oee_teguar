logger = system.util.getLogger("OEE_TEGUAR")

def internalFrameActivated(event):
	updateChartData()
	# # Kevon Code
	# dsDelta = system.tag.readBlocking('[client]template/deltaPercentData')[ 0 ].value
	# lineNumber = system.tag.readBlocking('[client]line_info/lineNumber')[ 0 ].value
	# # Set rawdata
	# print "Dopwntime internalFrameActivated: ", lineNumber, dsDelta
	# rowsToDelete = [i for i in range(dsDelta.getRowCount()) if dsDelta.getValueAt(i,'lineNumber') != lineNumber]
	# dsDeltaRaw = system.dataset.deleteRows(dsDelta, rowsToDelete)
	# rc = system.gui.getParentWindow(event).getRootContainer()
	# rc.deltaPercentData = dsDeltaRaw
	return


def downtimeWatchdog():
	def closeWindows():
		windowNames = ["Downtime/DowntimeEntryEditor"
					   ,"Downtime/ManualDowntimePopup"
					   ,"SOC/HTMLSOCPopup"
					   ]
		for windowName in windowNames:
			system.nav.closeWindow(windowName)
		return
	providerRemote = system.tag.readBlocking(["[client]line_info/providerRemote"])[0].value
	lineNumber = system.tag.readBlocking(["[client]line_info/lineNumber"])[0].value
	triggerPath = "[default]OT/SOC/{}/Downtime/NewDownTimeTrigger_L{}".format(providerRemote, lineNumber)
	if system.tag.readBlocking([triggerPath])[0].value:
		eventIdPath = "[default]OT/SOC/{}/Downtime/NewDownTimeID_L{}".format(providerRemote,lineNumber)
		eventID = system.tag.readBlocking([eventIdPath])[0].value
		params = {"eventID": eventID}
		eventData = system.db.runNamedQuery("GMS/Downtime/GetDowntimeEventByID",params)
		if eventData.getValueAt(0,"ParentEventCode") == 1:  # Generic event
			closeWindows()
			windows = system.gui.getOpenedWindowNames()
			window_params = {"downtimeID": eventID,"downtimeEvent": eventData}
			if eventData.getValueAt(0,"EventCode") in (101,105,106,107):  # Changeover
				if "Downtime/AutoChangeoverPopup" not in windows:
					window = system.nav.openWindow("Downtime/AutoChangeoverPopup", window_params)
			elif eventData.getValueAt(0,"EventCode") in (100,102,103,104):  # Non-Changeover
				if "Downtime/AutoDowntimePopup" not in windows:
					window = system.nav.openWindow("Downtime/AutoDowntimePopup", window_params)
	return


def shutdownIntercept(event):
	def confirmExit():
		""" Implements a custom dialog using java swing, JOptionPane
			See java documentation:
				https://docs.oracle.com/javase/tutorial/uiswing/components/dialog.html
				https://docs.oracle.com/en/java/javase/11/docs/api/java.desktop/javax/swing/JOptionPane.html
		"""
		from javax.swing import JOptionPane
		pane = JOptionPane()
		frame = None
		message = "An active downtime event exists.\n" \
				  + "<HTML><B>You must close the event first!</B>\n" \
				  + "Enter password to exit anyway.."
		title = "Cannot close window."
		messageType = pane.WARNING_MESSAGE
		result = pane.showInputDialog(frame,message,title,messageType)
		if result == "exit":
			return "exit"
		elif result == "close":
			return "close"
		return None

	windows = system.gui.getOpenedWindowNames()
	if "Downtime/AutoDowntimePopup" in windows or "Downtime/AutoChangeoverPopup" in windows:
		exitCode = confirmExit()
		if exitCode == "exit":
			pass
		elif exitCode == "close":
			event.cancel = 1
			system.nav.closeWindow("Downtime/AutoChangeoverPopup")
			system.nav.closeWindow("Downtime/AutoDowntimePopup")
		else:
			event.cancel = 1
	return


def getActionItems(dataset, lineNumber):
	if dataset is None:
		return
	#Filter action items by line
	rowsToDelete = []
	for idx in range(dataset.getRowCount()):
		if dataset.getValueAt(idx, 'Line') != lineNumber:
			rowsToDelete.append(idx)
	dsFiltered = system.dataset.deleteRows(dataset, rowsToDelete)
	return dsFiltered


def btnOpenSoc(event):
	""" Generate HTML from SOC data
	"""
	glass_db = oee.util.get_glass_db()
	socID = event.source.socID
	# Default message using markdown
	html = "# SOC Does Not Exist!\n### Notify Process Personnel."
	params = { 'socID': socID, "database": glass_db }
	# ds_html = system.db.runNamedQuery('GMS/Downtime/getHTMLReportBySOC_SP', params)
	# html = ds_html.getValueAt(0,0)
	html = oee.html.getHTML(glass_db, socID)
	if html is not None:
		window = system.nav.openWindow('SOC/HTMLSOCPopup',{ 'html': html })
		system.nav.centerWindow(window)
	return


def btnStartNewEvent(event):
	locationName = event.source.parent.locationName
	orderNumber = event.source.orderNumber
	window = system.nav.openWindow('Downtime/ManualDowntimePopup',{ 'locationName': locationName,'orderNumber': orderNumber })
	system.nav.centerWindow(window)
	return


def btnReviewEvents(event):
	lineNumber = event.source.parent.parent.lineNumber
	plantName = event.source.parent.parent.plantName
	window = system.nav.openWindow('Downtime/DowntimeEntryEditor',{ 'lineNumber': lineNumber,'plantName': plantName })
	system.nav.centerWindow(window)
	return


def getSeriesProperties(seriesName):
	headers = [ "SeriesName", "Value", "Color" ]
	data = [
			[seriesName, 0, system.gui.color("#8AFF8A")],
			[seriesName, 1, system.gui.color("#FF8AFF")],
			[seriesName, 2, system.gui.color("#FF8A8A")],
			[seriesName, 3, system.gui.color("#D9D900")]
			]
	return system.dataset.toDataSet(headers, data)


def btn_chartData(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	cntDowntime = event.source.parent
	startTime = cntDowntime.startTime
	seriesName = "Line {}".format(rc.lineNumber)
	kwargs = {
		"sourceID": rc.sourceID,
		"plantID": rc.plantID,
		"lineNumber": rc.lineNumber,
		"startDate": system.date.format(startTime, "yyyy-MM-dd HH:mm:ss"),
		"seriesName": seriesName,
	}
	qry = """
	SELECT TOP(100)
		StartTime AS t_stamp
		,CASE
			WHEN b.ParentEventCode = 0 THEN 0 --'Running'
			WHEN b.ParentEventCode = 2 THEN 1 --'Planned Downtime'
			WHEN b.ParentEventCode = 3 THEN 2 --'Unplanned Downtime'
			ELSE 3 --'Error in parent code'
		END AS [{seriesName}]
	FROM soc.DowntimeEvents a
	JOIN soc.DowntimeCodes b
		ON a.EventCode = b.EventCode
	WHERE sourceID = {sourceID}
		AND plantID = {plantID}
		AND lineNumber = {lineNumber}
		AND ( EndTime > '{startDate}' OR EndTime IS NULL)
	ORDER BY a.StartTime ASC
	""".format( **kwargs )
	#glass_db = oee.db.get_glass_db()
	glass_db = "glass"
	ds = system.db.runQuery(qry, glass_db)
	lastState = ds.getValueAt( ds.rowCount - 1, 1)
	dsFinal = system.dataset.addRow(ds, [system.date.now(), lastState])
	chart = cntDowntime.getComponent("Status Chart")
	chart.data = dsFinal
	chart.properties = getSeriesProperties(seriesName)
	return


def updateChartData():
	def runQuery(params, glass_db):
		qry = """
		SELECT TOP(100)
			[StartTime] AS t_stamp
			,CASE
				WHEN b.ParentEventCode = 0 THEN 0 --'Running'
				WHEN b.ParentEventCode = 2 THEN 1 --'Planned Downtime'
				WHEN b.ParentEventCode = 3 THEN 2 --'Unplanned Downtime'
				ELSE 3 --'Error in parent code'
			END AS [{seriesName}]
		FROM soc.DowntimeEvents a
		JOIN soc.DowntimeCodes b
			ON a.EventCode = b.EventCode
		WHERE sourceID = {sourceID}
			AND plantID = {plantID}
			AND lineNumber = {lineNumber}
			AND ( EndTime > '{startDate}' OR EndTime IS NULL)
		ORDER BY a.StartTime ASC
		""".format(**params)
		pyds = system.db.runQuery(qry, glass_db)
		return pyds

	args = {
		"sourceID": None,
		"plantID": None,
		"lineNumber": None
	}
	tag_names = args.keys()
	tag_paths = [ "[client]line_info/%s" % tag_name for tag_name in tag_names ]
	objs = system.tag.readBlocking(tag_paths)
	for tag_key, obj in zip(tag_names, objs):
		args[tag_key] = obj.value
	args["seriesName"] = "Line {}".format(args["lineNumber"])
	startTime = system.date.addHours( system.date.now(), -24)
	args["startDate"] = system.date.format(startTime,"yyyy-MM-dd HH:mm:ss")
	glass_db = "glass"
	py = runQuery(args, glass_db)

	if py.rowCount > 0:
		lastState = py.getValueAt( py.rowCount - 1, 1)
		chartData = system.dataset.addRow(py, [system.date.now(), lastState])
		chartProperties = getSeriesProperties(args["seriesName"])
		system.tag.writeBlocking(["[client]downtime/chartData",
								  "[client]downtime/chartProperties"],
								 [chartData,
								 chartProperties
								  ])
	# compare_to_live = True
	# if compare_to_live:
	# 	glass_db = oee.db.get_glass_db()
	# 	py_live = runQuery(args, glass_db)
	# 	lastState = py_live.getValueAt(py_live.rowCount - 1,1)
	# 	chartData = system.dataset.addRow(py_live,[ system.date.now(),lastState ])
	# 	system.tag.writeBlocking([ "[client]downtime/test_chartData",
	# 							   "[client]downtime/test_chartProperties" ],
	# 							 [ chartData,
	# 							   chartProperties
	# 							   ])
	return


def updateChartDetailData():
	"""
	Runs cross apply query to get sequential downtime data.
	Processes data to create individual series per event.
	Creates color mapping for properties.

	Creates two datasets
	chartData:
		t_stamp, {seriesName}
	chartProperties
		{seriesName}, color
	"""

	def getSeriesProperties(chart_data, eventData):
		def getColor(eventData,series,value, order_colors_used):
			#global order_colors_used
			obj = system.gui.color(250,250,251)
			if series == "Order":
				colorOffset = 10 + ( len(order_colors_used) * 50 )
				obj = system.gui.color(colorOffset,colorOffset,255,255)
				order_colors_used.append(obj)
			elif value == 9999:
				obj = system.gui.color(255,255,255,1)
			else:
				for idx in range(eventData.rowCount):
					if eventData.getValueAt(idx,"EventCode") == value:
						obj = system.gui.color(eventData.getValueAt(idx,"color"))
			return obj

		order_colors_used = []
		headers = [ "SeriesName","Value","Color" ]
		seriesList = list(chart_data.columnNames)
		rows = [ ]
		for series in seriesList[ 1: ]:
			values = list(set(int(chart_data.getValueAt(i,series)) for i in range(chart_data.rowCount)))
			for value in values:
				color_obj = getColor(eventData,series,value, order_colors_used)
				rows.append( [ series,value,color_obj ] )
		dsProperties = system.dataset.toDataSet(headers,rows)
		return dsProperties

	args = {
		"sourceID": None,
		"plantID": None,
		"lineNumber": None
	}
	tag_names = args.keys()
	tag_paths = [ "[client]line_info/%s" % tag_name for tag_name in tag_names ]
	objs = system.tag.readBlocking(tag_paths)
	for tag_key, obj in zip(tag_names, objs):
		args[tag_key] = obj.value
	startTime = system.date.addHours( system.date.now(), -24)
	args["startDate"] = system.date.format(startTime,"yyyy-MM-dd HH:mm:ss")
	args["database"] = "glass"
	eventData = system.db.runNamedQuery("Downtime/chartData", args)
	# Create base series for line
	lineSeries = "Line {}".format(args["lineNumber"])
	columnNames = [ "t_stamp", lineSeries, "Order" ]
	seriesNames =  list(set( eventData.getValueAt( i, "seriesName" ) for i in range( eventData.rowCount ) ))
	rows = []
	for idx in range( eventData.rowCount ):
		row = [eventData.getValueAt( idx, "t_stamp" ), eventData.getValueAt( idx, "EventCode" ), eventData.getValueAt( idx, "orderNumber" )]
		for seriesName in seriesNames:
			if eventData.getValueAt( idx, "seriesName" ) == seriesName:
				row.append( eventData.getValueAt( idx, "EventCode" ) )
			else:
				row.append( 9999 )
		rows.append( row )
	columnNames.extend(seriesNames)
	chartData = system.dataset.toDataSet( columnNames, rows )
	chartProperties = getSeriesProperties(chartData, eventData)
	system.tag.writeBlocking(["[client]downtime/chartData",
							  "[client]downtime/chartProperties"],
							 [chartData,
							 chartProperties
							  ])
	return


def getChartToolTipText(self,seriesIndex,selectedTimeStamp,timeDiff,selectedStatus,data,properties,defaultString):
	"""
	Returns a formatted tool tip String.

	Arguments:
		self: A reference to the component that is invoking this function.
		seriesIndex: The series index corresponding to the column in the
					 series dataset.
		selectedTimeStamp: The time stamp corresponding to the x value of the
						   displayed tooltip. The time stamp is the number of seconds since the
						   epoch.
		timeDiff: The width of the current status interval measured in seconds
				  since the epoch.
		selectedStatus: The status value corresponding to the x value of the
						displayed tooltip.
		data: The series dataset as a PyDataset.
		properties: The series properties dataset as a PyDataset.
		defaultString: The default tooltip string.
	"""
	# return defaultString
	# Break the default string apart and extract the start date and the end date

	def getEventName(events, eventCode):
		for row in events:
			if row["EventCode"] == eventCode:
				parentName = row["ParentEventName"]
				if parentName == "Running" or parentName == "Generic Downtime":
					return row["Name"]
				else:
					return "{}: {}: {}".format( parentName, row["Category"], row["Name"] )
		return "{} Not Found".format( eventCode )

	def getOrderNumber():
		startingIndex = defaultString.index('(') + 1
		endingIndex = defaultString.index(')')
		datetimes = defaultString[ startingIndex: endingIndex ].split(',')
		startDate = system.date.parse(datetimes[ 0 ] + datetimes[ 1 ],'MM/dd/yy hh:mm a')
		downtime = self.parent.downtime
		for idx in range(downtime.rowCount):
			chart_date_string = system.date.format(startDate, "MM/dd/yy HH:mm a")
			event_date_string = system.date.format(downtime.getValueAt( idx, "StartTime"), "MM/dd/yy HH:mm a")
			if chart_date_string == event_date_string:
				return downtime.getValueAt( idx, "orderNumber" )
		return "Order Number Not Found"

	if selectedStatus < 1000:
		# print 'selectedStatus',selectedStatus
		# Replace seriesName: "EventCode" with actual event name.
		events = system.dataset.toPyDataSet(self.parent.downtime)
		eventName = getEventName(events, selectedStatus)
		customString = defaultString.replace("EventCode", eventName)
		# Add order number
		customString = "{orderNumber}: {existingString}".format( orderNumber=getOrderNumber(), existingString=customString )
		return customString
	else:
		return "Order Number: {}, Duration: {} Hours".format(selectedStatus, oee.util.round_half_up(timeDiff/3600.0, decimals=1))


def root_container_propertyChange(event):
	if event.propertyName == "newDowntimeTrigger":
		newDowntimeTrigger(event)
	return


def newDowntimeTrigger(event):
	if event.propertyName == "newDowntimeTrigger":
		print "newDowntimeTrigger: ", event.newValue, system.date.now()
		if event.newValue:
			eventID = system.gui.getParentWindow(event).getComponentForPath('Root Container').downtimeID
			db_params = { "eventID": eventID }
			eventData = system.db.runNamedQuery("GMS/Downtime/GetDowntimeEventByID",db_params)
			window_params = {"downtimeID": eventID, "downtimeEvent": eventData}
			if eventData.getValueAt(0,"EventCode") in (101,105,106,107): # Changeover
				window = system.nav.openWindow("Downtime/AutoChangeoverPopup", window_params)
			else:
				window = system.nav.openWindow("Downtime/AutoDowntimePopup", window_params)
			# system.nav.centerWindow(window)
	return


def changeLine(event):
	if oee.landing.is_developer():
		window = system.nav.openWindow("Landing")
		system.nav.centerWindow(window)
	return