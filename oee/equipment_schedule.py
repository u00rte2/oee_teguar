def get_items_events(eventData, args):
	"""
	:return: dataset
		columns
			 ID
			 Label
			 StatusImageIcon
			 Foreground
			 Background
	"""
	headers = [	"ID", "Label", "StatusImageIcon", "Foreground", "Background" ]
	row = [
		args["lineNumber"],
		"Line {lineNumber}".format(**args),
		"Builtin/icons/24/media_play.png",
		system.gui.color("white"),
		system.gui.color("8AFF8A")
	]
	itemData = system().dataset.toDataSet(headers, [row])
	return itemData


def getScheduledEvents(eventData, args):
	"""
	:return: dataset
		columns
			 EventID
			 ItemID
			 StartDate
			 EndDate
			 Label
			 Foreground
			 Background
			 LeadTime
			 LeadColor
			 PctDone
	"""
	def getDate(ds, value, minmax):
		eventDate = None
		for idx in range(ds.rowCount):
			if ds.getValueAt(idx, "orderNumber") == value:
				if minmax == "min":
					if eventDate is None or ds.getValueAt(idx, "t_stamp") < eventDate:
						eventDate = ds.getValueAt(idx, "t_stamp")
				if minmax == "max":
					if eventDate is None or ds.getValueAt(idx, "t_stamp") > eventDate:
						eventDate = ds.getValueAt(idx, "t_stamp")
		return eventDate
	orderNumbers = list(set(row["OrderNumber"] for row in range(eventData.rowCount)))
	rows = []
	for orderNumber in orderNumbers:
		row = [orderNumber, 									# EventID
				args[ "lineNumber" ],							# ItemID
				getDate(eventData, orderNumber, "min"),	# StartDate
				getDate(eventData, orderNumber, "max"),	# EndDate
				str(orderNumber),								# Label
				system.gui.color("black"),						# Foreground
				system.gui.color("white"),						# Background
				0,												# LeadTime
				system.gui.color("yellow"),						# LeadColor
				0												# PctDone
			]
		rows.append(row)
	headers = [	"EventID", "ItemID", "StartDate", "EndDate", "Label", "Foreground", "Background", "LeadTime", "LeadColor", "PctDone"]
	return system.dataset.toDataSet(headers, rows)


def getDowntimeEvents(eventData, args):
	"""
	:return: dataset
		columns
			 ItemID
			 StartDate
			 EndDate
			 Color
			 Layer
	"""


	return


def getBreakEvents():
	"""
	:return: dataset
		columns
			 StartDate
			 EndDate
			 Color
	"""
	return
