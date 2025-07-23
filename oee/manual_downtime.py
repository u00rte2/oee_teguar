def internalFrameActivated(event):
	oee.auto_downtime.resetStates(event)
	return


def msbtn_downtimeEventType(event):
	if event.propertyName == "controlValue":
		print('msbtn_downtimeEventType', event.propertyName,event.newValue,event.oldValue)
		PLANNED_CONTROL_VALUE = 0
		UNPLANNED_CONTROL_VALUE = 1
		RUNNING_CONTROL_VALUE = 2
		print 'msbtn_downtimeEventType', event.newValue
		rc = event.source.parent
		rc.getComponent('Dropdown').selectedIndex = -1
		rc.category = ''
		if event.newValue == RUNNING_CONTROL_VALUE:
			print "Mode: Running"
			rc.getComponent('msbtn_downtimeSubEventType').states = None
			rc.mode = 'Running'
			rc.getComponent('Dropdown').visible = 0
			rc.getComponent('Dropdown').selectedIndex = -1
			rc.getComponent('txtFldOtherField').visible = 1
			rc.getComponent('txtFldOtherField').text = ''
			rc.getComponent('lbl_OtherFieldCaption').visible = 1
			rc.getComponent('lbl_OtherFieldCaption').text = "Enter Running Restart Reason"
		else:
			print "Mode: else"
			if event.newValue == PLANNED_CONTROL_VALUE:
				rc.getComponent('msbtn_downtimeSubEventType').states = rc.plannedStates
				rc.mode = 'Planned Downtime'
			elif event.newValue == UNPLANNED_CONTROL_VALUE:
				rc.getComponent('msbtn_downtimeSubEventType').states = rc.unplannedStates
				rc.mode = 'Unplanned Downtime'
			rc.getComponent('txtFldOtherField').visible = 0
			rc.getComponent('txtFldOtherField').text = ''
			rc.getComponent('lbl_OtherFieldCaption').visible = 0
			rc.getComponent('lbl_OtherFieldCaption').text = ""
		rc.getComponent('txtFldNotesField').text = ""
	return


def msbtn_downtimeSubEventType(event):
	if event.propertyName == "controlValue":
		print(event.propertyName, event.newValue, event.oldValue)
		if event.newValue != event.oldValue and event.newValue > -1:
			rc = event.source.parent
			states = event.source.states
			options = [ ]
			cat = ''
			for i in range(states.rowCount):
				if states.getValueAt(i, "value") == event.newValue:
					cat = states.getValueAt(i, "selectedText")
			if cat != '':
				if cat == 'Other':
					rc.category = 'Other'
					rc.getComponent('txtFldOtherField').visible = 1
					rc.getComponent('Dropdown').visible = 0
					rc.getComponent('Dropdown').selectedIndex = -1
					rc.getComponent('lbl_OtherFieldCaption').visible = 1
					rc.getComponent('lbl_OtherFieldCaption').text = "Enter Downtime Reason"
				else:
					rc.category = 'Valid'
					params = { 'Category': cat }
					categories = oee.db.runNamedQuery('GMS/Downtime/GetDowntimeCodesByCategory',params)
					for i in range(categories.rowCount):
						name = categories.getValueAt(i,'Name')
						val = categories.getValueAt(i,'ID')
						options.append([val, name])
					dd_options = system.dataset.toDataSet(["value", "label"] , options)
					rc.getComponent('Dropdown').data = dd_options
					rc.getComponent('Dropdown').visible = 1
					rc.getComponent('Dropdown').selectedIndex = -1
					rc.getComponent('txtFldOtherField').visible = 0
					rc.getComponent('lbl_OtherFieldCaption').visible = 0
					rc.getComponent('lbl_OtherFieldCaption').text = ""
	return


def btn_submit(event):
	self = event.source
	rc = self.parent
	other_reason = ""
	codeID = -1
	if rc.category == 'Other':
		if rc.mode == 'Planned Downtime':
			codeID = 3
		elif rc.mode == 'Unplanned Downtime':
			codeID = 19
		other_reason = rc.getComponent('txtFldOtherField').text
	else:
		if rc.mode == 'Running':
			codeID = 1
			other_reason = rc.getComponent('txtFldOtherField').text
		else:
			codeID = rc.getComponent('Dropdown').selectedValue
	note = "{other_reason}-{note}".format(other_reason=other_reason,note=rc.getComponent('txtFldNotesField').text)
	eventObj = oee.db.runNamedQuery('GMS/Downtime/GetDowntimeCodeByID', { 'ID': codeID })
	eventCode = eventObj.getValueAt(0,'EventCode')
	version = eventObj.getValueAt(0,'Version')
	now = system.date.now()
	# Check if last event was generic downtime
	params = { 'LocationName': rc.locationName }
	mostRecentEvent = system.db.runNamedQuery('GMS/Downtime/GetMostRecentEvent',params)
	mostRecentCode = None
	if mostRecentEvent is not None and mostRecentEvent.rowCount > 0:
		mostRecentID = mostRecentEvent.getValueAt(0,'ID')
		mostRecentCode = mostRecentEvent.getValueAt(0,'EventCode')
	# If generic then
	if mostRecentCode is not None and int(mostRecentCode) == 1 and eventCode != 0:
		# Update generic downtime to new event
		params = { 'ID': mostRecentID,
				   'CreatedBy': "ManualDowntimePopupSubmit",
				   'EventCode': eventCode,
				   'Version': version,
				   'Note': note,
				   'IsManual': True
				   }
		oee.db.runNamedQuery('GMS/Downtime/UpdateDowntimeEventByID',params)
	else:
		# End old event and start new one from end time
		params = { 'EndTime': now,'LocationName': rc.locationName }
		system.db.runNamedQuery('GMS/Downtime/EndCurrentDowntimeEvent',params)
		params = { 'LocationName': rc.locationName,
				   'EventCode': eventCode,
				   'Version': version,
				   'CreatedBy': "ManualDowntimePopup",
				   'StartTime': now,
				   'Note': note,
				   'Shift': "Shift A",
				   'WorkOrder': rc.orderNumber,
				   "sourceID": rc.sourceID,
				   "plantID": rc.plantID,
				   "lineLinkID": rc.lineLinkID,
				   "lineNumber": rc.lineNumber
				   }
		system.db.runNamedQuery('GMS/Downtime/BasicStartManualDowntimeEvent',params)
	system.nav.closeParentWindow(event)
	return