systemName = system.tag.readBlocking('[System]Gateway/SystemName')[0].value

def readme():
	"""
	Named Queries used in Perspective App

	Path											Where Used
	GMS/Downtime/GetDowntimeEventsInBetweenTime		GMS/Downtime
	GMS/Downtime/GetMostRecentEventCode				GMS/Downtime
	GMS/Downtime/GetDowntimeCodeName				GMS/Downtime
	GMS/Downtime/GetDowntimeEventsForTimeRange		GMS/Components/DowntimeEntryEditor

	getHTMLReportBySOC_SP							oee.views.downtime.root_table_title_button_onClick

	GMS/Downtime/UpdateDowntimeEventByID			oee.views.auto_downtime.root_timer_label_custom_secs_left
													oee.views.auto_downtime.root_footer_submit
													oee.views.manual_downtime.root_footer_submit

	GMS/Downtime/GetDowntimeCodesByCategory			oee.views.auto_downtime.root_subevents_planned_buttons_props_indicator_value
													oee.views.auto_downtime.root_subevents_unplanned_buttons_props_indicator_value
													oee.views.manual_downtime.root_subevents_planned_buttons_props_indicator_value
													oee.views.manual_downtime.root_subevents_unplanned_buttons_props_indicator_value

	GMS/Downtime/GetDowntimeCodeByID				oee.views.auto_downtime.root_footer_submit
													oee.views.manual_downtime.root_footer_submit

	GMS/Downtime/GetMostRecentEvent					oee.views.manual_downtime.root_footer_submit

	GMS/Downtime/UpdateDowntimeEventByID			oee.views.manual_downtime.root_footer_submit

	GMS/Downtime/BasicStartManualDowntimeEvent		oee.views.manual_downtime.root_footer_submit
	"""
	return

def get_glass_db():
	if systemName == 'Ignition-BLM-SQL02':
		glass_db = "glass_cnfsql04"
	else:
		glass_db = "glass"
	return glass_db


def get_categories(parent_code):
	params = { 'ParentEventCode': parent_code }
	dsCategories = system.db.runNamedQuery('GMS/Downtime/GetDowntimeCategoriesByParentCode', params)
	headers = oee.util.multistate_button_default_header()
	newRows = []
	if dsCategories.rowCount > 0:
		for idx in range(dsCategories.rowCount):
			if dsCategories.getValueAt(idx, "Category") != "":
				data = oee.util.multistate_button_default_rowDict()
				data["value"] = idx
				data[ "selectedText" ] = dsCategories.getValueAt(idx, "Category")
				data[ "unselectedText" ] = dsCategories.getValueAt(idx, "Category")
				newRows.append( [ data[ col ] for col in headers ] )
		dsOut = system.dataset.toDataSet(headers , newRows)
	else:
		dsOut = system.dataset.toDataSet(headers, [ None for i in range(len(headers)) ] )
	return dsOut


def runNamedQuery(qry, params):
	""" Wrapper to intercept db changes without rights
	:param qry: String, path to named query
	:param params: dictionary, parameters to pass to named query
	:return: Nothing,
	"""
	result = None
	rights = system.tag.readBlocking("[client]user/rights")[0].value
	if "Update" in qry or "BasicStart" in qry:
		if "edit" in rights:
			print "runNamedQuery, {}".format(params)
			result = system.db.runNamedQuery(qry, params)
		else:
			print(qry)
			print(params)
	else:
		result = system.db.runNamedQuery(qry,params)
	return result


def get_chart_events():
	"""

	:return: dataset
		columns:
			t_stamp
			EventCode
			ParentEventCode
			orderNumber
			seriesName
			color
	"""
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
	system.tag.writeBlocking([ "[client]downtime/chartEvents"], [ eventData ])
	return eventData, args