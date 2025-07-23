def internalFrameActivated(event):
	resetTimer(event)
	resetStates(event)
	return


def resetStates(event):
	print "resetStates"
	rc = system.gui.getParentWindow(event).getRootContainer()
	PLANNED_PARENT_CODE = 2
	UNPLANNED_PARENT_CODE = 3
	rc.mode = ''
	rc.category = ''
	rc.getComponent("msbtn_downtimeEventType").controlValue = -1
	rc.getComponent("msbtn_downtimeSubEventType").controlValue = -1
	rc.getComponent('txtFldOtherField').visible = 0
	rc.getComponent('txtFldOtherField').text = ""
	rc.getComponent('Dropdown').visible = 0
	rc.getComponent('Dropdown').selectedIndex = -1
	rc.getComponent('txtFldNotesField').text = ""
	rc.plannedStates = oee.db.get_categories(PLANNED_PARENT_CODE)
	rc.unplannedStates = oee.db.get_categories(UNPLANNED_PARENT_CODE)
	return


def resetTimer(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	timer = rc.getComponent("Timer")
	timer.max = 2400
	timer.value = 0
	timer.running = 1
	return


def timer_propertyChange(event):
	if event.propertyName == "value":
		self = event.source
		rc = self.parent
		if self.value == 2400:
			if system.tag.readBlocking("[System]Gateway/SystemName")[0].value == "Ignition-BLM-SQL02":
				resetTimer(event)
				return
			# if timer runs out, mark downtime event as "operator error"
			ID = rc.downtimeID
			createdBy = 'AutoDowntimePopupTimer'
			eventCode = 315
			version = 1
			note = ''
			params = { 'ID': ID, 'CreatedBy': createdBy, 'EventCode': eventCode, 'Version': version, 'Note': note, 'IsManual': False }
			#oee.db.runNamedQuery("GMS/Downtime/UpdateDowntimeEventByID", params)
			#system.nav.closeParentWindow(event)
	return


def msbtn_downtimeEventType(event):
	if event.propertyName == "controlValue":
		PLANNED_CONTROL_VALUE = 0
		UNPLANNED_CONTROL_VALUE = 1
		rc = event.source.parent
		if event.newValue == PLANNED_CONTROL_VALUE:
			rc.getComponent('msbtn_downtimeSubEventType').states = rc.plannedStates
			rc.mode = 'Planned Downtime'
		elif event.newValue == UNPLANNED_CONTROL_VALUE:
			rc.getComponent('msbtn_downtimeSubEventType').states = rc.unplannedStates
			rc.mode = 'Unplanned Downtime'
		print(event.newValue, rc.mode)
		rc.getComponent('Dropdown').selectedIndex = -1
		rc.category = ''
		rc.getComponent('txtFldOtherField').text = ''
		rc.getComponent('lbl_OtherFieldCaption').visible = 0
		rc.getComponent('lbl_OtherFieldCaption').text = ""
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
				if states.getValueAt(i, "value") == event.newValue :
					cat = states.getValueAt(i, "selectedText")
			if cat != '':
				if cat == 'Other':
					rc.category = 'Other'
					rc.getComponent('txtFldOtherField').visible = 1
					rc.getComponent('Dropdown').visible = 0
					rc.getComponent('Dropdown').selectedIndex = -1
					rc.getComponent('lbl_OtherFieldCaption').visible = 1
					rc.getComponent('lbl_OtherFieldCaption').text = "Enter Downtime Reason"
					rc.getComponent('txtFldNotesField').text = ""
					rc.getComponent('txtFldOtherField').text = ''
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
	note = rc.getComponent('txtFldNotesField').text
	other_reason = ""
	codeID = -1
	if rc.category == 'Other':
		if rc.mode == 'Planned Downtime':
			codeID = 3
		elif rc.mode == 'Unplanned Downtime':
			codeID = 19
		other_reason = rc.getComponent('txtFldOtherField').text
	else:
		codeID = rc.getComponent('Dropdown').selectedValue
	eventObj = oee.db.runNamedQuery('GMS/Downtime/GetDowntimeCodeByID', { 'ID': codeID })
	params = { 'ID': rc.downtimeID,
			   'CreatedBy': "AutoDowntimePopupSubmit",
			   'EventCode': eventObj.getValueAt(0,'EventCode'),
			   'Version': eventObj.getValueAt(0,'Version'),
			   'Note': "{other_reason}-{note}".format(other_reason=other_reason, note=note),
			   'IsManual': False
			   }
	oee.db.runNamedQuery('GMS/Downtime/UpdateDowntimeEventByID', params)
	downtimeWindow = system.gui.getWindow("Downtime/Downtime_Main")
	downtimeWindow.getRootContainer().newDowntimeTrigger = False
	system.nav.closeParentWindow(event)
	return