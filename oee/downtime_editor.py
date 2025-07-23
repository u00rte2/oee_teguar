PLANNED_PARENT_CODE = 2
UNPLANNED_PARENT_CODE = 3

def readMe():
	"""

	Query: GMS/Downtime/GetDowntimeEventsForTimeRange
	last 7 days


	if({Root Container.tbl_events.selectedRow} != -1, {Root Container.tbl_events.data}[{Root Container.tbl_events.selectedRow},"Name"], '')

	:return:
	"""
	return

def internalFrameActivated(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	rc.dropdownsEnabled = False
	rc.plannedStates = oee.db.get_categories(PLANNED_PARENT_CODE)
	rc.unplannedStates = oee.db.get_categories(UNPLANNED_PARENT_CODE)
	rc.getComponent("startTime").date = system.date.addDays( system.date.now(), -7)
	rc.getComponent("endTime").date = system.date.now()
	return


def resetDetailComponents(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	cntDetail = rc.getComponent("cntDetail")
	cntDetail.getComponent("val_category").text = ""
	cntDetail.getComponent("val_description").text = ""
	cntDetail.getComponent("val_note").text = ""
	cntDetail.getComponent("val_orderNumber").text = ""
	cntDetail.getComponent("val_originalCreatedBy").text = ""
	cntDetail.getComponent("val_parentType").text = ""
	cntDetail.getComponent("val_shift").text = ""
	cntDetail.getComponent("chk_manual").selected = False
	cntDetail.getComponent("chk_downtime").selected = False
	cntDetail.getComponent("chk_planned").selected = False
	cntDetail.getComponent("chk_changeover").selected = False
	return


def resetEditComponents(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	rc.dropdownsEnabled = False
	cntEdit = rc.getComponent("cntEdit")
	cntEdit.getComponent("valID").value = -1
	cntEdit.getComponent("valCurrentEvent").text = ""
	cntEdit.getComponent("ddParentCode").selectedValue = -1
	cntEdit.getComponent("ddCategory").selectedValue = -1
	cntEdit.getComponent("ddNewDowntimeEvent").selectedValue = -1
	cntEdit.getComponent("valNote").text = ""
	return


def tblEvents_propertyChange(event):
	if event.propertyName == "selectedRow":
		self = event.source
		rc = self.parent
		selectedRow = self.selectedRow
		rc.dropdownsEnabled = False
		if selectedRow == -1:
			resetDetailComponents(event)
		else:
			# Selected Event From Table
			print 'tblEvents_propertyChange'
			data = self.data
			parentcode = data.getValueAt(selectedRow,"ParentEventCode")
			cntDetail = rc.getComponent("cntDetail")
			cntDetail.getComponent("val_category").text = data.getValueAt(selectedRow, "Category")
			cntDetail.getComponent("val_description").text = data.getValueAt(selectedRow, "Description")
			cntDetail.getComponent("val_note").text = data.getValueAt(selectedRow, "Note")
			cntDetail.getComponent("val_orderNumber").text = data.getValueAt(selectedRow, "WorkOrderUUID")
			cntDetail.getComponent("val_originalCreatedBy").text = data.getValueAt(selectedRow, "OriginalCreatedBy")
			cntDetail.getComponent("val_parentType").text = data.getValueAt(selectedRow, "ParentEventName")
			cntDetail.getComponent("val_parentCode").value = parentcode
			cntDetail.getComponent("val_eventName").text = data.getValueAt(selectedRow,"Name")
			cntDetail.getComponent("val_shift").text = data.getValueAt(selectedRow, "Shift")
			cntDetail.getComponent("chk_manual").selected = data.getValueAt(selectedRow, "IsManual")
			cntDetail.getComponent("chk_downtime").selected = data.getValueAt(selectedRow, "IsDowntime")
			cntDetail.getComponent("chk_planned").selected = data.getValueAt(selectedRow, "IsPlanned")
			cntDetail.getComponent("chk_changeover").selected = data.getValueAt(selectedRow,"IsChangeoverDowntime")
			cntDetail.getComponent("val_eventCode").value = data.getValueAt(selectedRow,"EventCode")
			cntDetail.getComponent("val_createdBy").text = data.getValueAt(selectedRow,"CreatedBy")
			cntDetail.getComponent("val_eventVersion").value = data.getValueAt(selectedRow,"EventCodeVersion")
			# Pre-populate data in cntEdit container
			cntEdit = rc.getComponent("cntEdit")
			enableEdits = False if data.getValueAt(selectedRow, "Name") == "Running" else True
			cntEdit.visible = enableEdits
			if enableEdits:
				print "enableEdits"
				cntEdit.getComponent("valID").value = data.getValueAt(selectedRow,"ID")
				cntEdit.getComponent("valCurrentEvent").text = data.getValueAt(selectedRow,"Name")
				cntEdit.getComponent("ddParentCode").selectedValue = parentcode
				if parentcode == PLANNED_PARENT_CODE:
					cntEdit.getComponent("ddCategory").data  = rc.plannedStates
				elif parentcode == UNPLANNED_PARENT_CODE:
					cntEdit.getComponent("ddCategory").data = rc.unplannedStates
				cntEdit.getComponent("ddCategory").selectedStringValue = data.getValueAt(selectedRow,"Category")
				params = { 'ParentEventCode': parentcode,'Category': data.getValueAt(selectedRow,"Category") }
				eventCodeOptions = system.db.runNamedQuery('GMS/Downtime/GetDowntimeCodesByCategoryAndParent',params)
				cntEdit.getComponent("ddNewDowntimeEvent").data = eventCodeOptions
				cntEdit.getComponent("ddNewDowntimeEvent").selectedValue = data.getValueAt(selectedRow,"EventCode")
				cntEdit.getComponent("valNote").text = data.getValueAt(selectedRow, "Note")
				def enable_dropdowns(rc=rc):
					rc.dropdownsEnabled = True
				system.util.invokeLater(enable_dropdowns, 200)
			else:
				resetEditComponents(event)
	return


def ddParentCode_propertyChange(event):
	if event.propertyName == "selectedValue":
		rc = system.gui.getParentWindow(event).getRootContainer()
		self = event.source
		cntEdit = self.parent
		parentcode = event.newValue
		if rc.dropdownsEnabled and event.propertyName == "selectedValue":
			if parentcode is not None and parentcode > 0:
				if parentcode == PLANNED_PARENT_CODE:
					cntEdit.getComponent("ddCategory").data = rc.plannedStates
				elif parentcode == UNPLANNED_PARENT_CODE:
					cntEdit.getComponent("ddCategory").data = rc.unplannedStates
				cntEdit.getComponent("ddCategory").selectedValue = -1
	return


def ddCategory_propertyChange(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	self = event.source
	cntEdit = self.parent
	category = event.newValue
	if rc.dropdownsEnabled and event.propertyName == "selectedStringValue":
		if category is not None and category != "":
			parentcode = cntEdit.getComponent("ddParentCode").selectedValue
			params = { 'ParentEventCode': parentcode,'Category': category }
			eventCodeOptions = system.db.runNamedQuery('GMS/Downtime/GetDowntimeCodesByCategoryAndParent',params)
			cntEdit.getComponent("ddNewDowntimeEvent").data = eventCodeOptions
			cntEdit.getComponent("ddNewDowntimeEvent").selectedValue = -1
	return


def btn_refresh(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	system.db.refresh(rc.getComponent('tbl_events'), "data")
	resetDetailComponents(event)
	resetEditComponents(event)
	rc.getComponent('tbl_events').selectedRow = -1
	return


def btn_submit(event):
	def change_made():
		if ( cntEdit.getComponent("ddParentCode").selectedValue != -1
				and cntEdit.getComponent("ddCategory").selectedValue != -1
				and cntEdit.getComponent("ddNewDowntimeEvent").selectedValue != -1
				and new_eventCode != -1
				and rc.dropdownsEnabled
				) and (cntDetail.getComponent("val_note").text != cntEdit.getComponent("valNote").text
						or new_eventCode != current_eventCode
						):
			return True
		return False

	rc = system.gui.getParentWindow(event).getRootContainer()
	current_eventCode = rc.getComponent("cntDetail").getComponent("val_eventCode").value
	cntDetail = rc.getComponent("cntDetail")
	cntEdit = rc.getComponent("cntEdit")
	new_eventCode = cntEdit.getComponent("ddNewDowntimeEvent").selectedValue
	if change_made():
		params = { "ID": cntEdit.getComponent("valID").value,
				   "EventCode": cntEdit.getComponent("ddNewDowntimeEvent").selectedValue,
				   "Version": cntDetail.getComponent("val_eventVersion").intValue + 1,
				   "CreatedBy": cntDetail.getComponent("val_createdBy").text,
				   "Note": cntEdit.getComponent("valNote").text,
				   "IsManual": cntDetail.getComponent("chk_manual").selected
				   }

		print params

		oee.db.runNamedQuery('GMS/Downtime/UpdateDowntimeEventByID',params)
		btn_refresh(event)
	return
