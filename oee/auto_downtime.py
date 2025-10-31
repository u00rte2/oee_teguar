def internalFrameActivated(event):
	resetTimer(event)
	resetStates(event)
	rc = system.gui.getParentWindow(event).getRootContainer()
	print "AutoDowntimeEvent: ", rc.downtimeID
	# rc.downtimeEvent = oee.db.runNamedQuery("GMS/Downtime/GetDowntimeEventByID",{"eventID": rc.downtimeID})
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


def commit_event(downtimeID, codeID, CreatedBy, note, changeover_text):
	eventObj = oee.db.runNamedQuery('GMS/Downtime/GetDowntimeCodeByID', { 'ID': codeID })
	params = { 'ID': downtimeID,
			   'CreatedBy': CreatedBy,
			   'EventCode': eventObj.getValueAt(0,'EventCode'),
			   'Version': eventObj.getValueAt(0,'Version'),
			   'Note': note,
			   'changeoverDetail': changeover_text,
			   'IsManual': False
			   }
	oee.db.runNamedQuery('GMS/Downtime/UpdateDowntimeEventByID', params)
	downtimeWindow = system.gui.getWindow("Downtime/Downtime_Main")
	downtimeWindow.getRootContainer().newDowntimeTrigger = False
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
	note = "{other_reason}-{note}".format(other_reason=other_reason,note=note)
	changeover_text = ""
	commit_event(rc.downtimeID,codeID,"AutoDowntimePopupSubmit",note,changeover_text)
	system.nav.closeParentWindow(event)
	return


def reset_changeover_selections(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	selectedCells = rc.getComponent('cnt_changeover').selectedCells
	for c in range(selectedCells.columnCount):
		if c > 0:
			for r in range(selectedCells.rowCount):
				selectedCells = system.dataset.setValue(selectedCells,r,c,False)
	rc.getComponent('cnt_changeover').selectedCells = selectedCells
	rc.changeover_level = 0
	return


def internalFrameActivated_changeover(event):
	reset_changeover_selections(event)
	rc = system.gui.getParentWindow(event).getRootContainer()
	print "AutoChangeoverEvent: ", rc.downtimeID
	# rc.downtimeEvent = oee.db.runNamedQuery("GMS/Downtime/GetDowntimeEventByID",{"eventID": rc.downtimeID})
	return


def getChangeoverLevel(event):
	rc = system.gui.getParentWindow(event).getRootContainer()
	ds = rc.getComponent('cnt_changeover').selectedCells
	levels = [ r+1 for r in range(ds.rowCount) for c in range(ds.columnCount) if c > 0 and ds.getValueAt(r,c) ]
	rc.changeover_level = max(levels) if len(levels) > 0 else 0
	return


def getChangeoverDetail(data, selectedCells):
	changeover_level = 0
	changeover_detail = ""
	for c in range(1, selectedCells.columnCount):
		colName = selectedCells.columnNames[c]
		for r in range(selectedCells.rowCount):
			if selectedCells.getValueAt(r,c):
				changeover_level = r + 1
				changeover_detail += "{}: {}\n".format(colName, data.getValueAt(r,c))
	return changeover_level, changeover_detail

def btn_submit_changeover(event):
	rc = event.source.parent
	changeover_codes = {1: 8,# 205,
						2: 9,# 206,
						3: 10,# 207,
						4: 11,# 208,
						5: 12,# 209,
						6: 13 # 210
						}
	selectedCells = rc.getComponent('cnt_changeover').selectedCells
	changeover_data = rc.getComponent('cnt_changeover').getComponent('tbl_changeover_def').data
	changeover_level = 0
	changeover_text = ""
	for c in range(selectedCells.columnCount):
		colName = selectedCells.columnNames[c]
		if c > 0:
			for r in range(selectedCells.rowCount):
				if selectedCells.getValueAt(r,c):
					changeover_level = r + 1
					changeover_text += "{}: {}\n".format(colName,changeover_data.getValueAt(r,c))
	changeoverCodeID = changeover_codes[changeover_level]
	note = "{notes}".format(notes=rc.getComponent('txtFldNotesField').text)
	commit_event(rc.downtimeID,changeoverCodeID,"AutoChangeoverPopupSubmit",note,changeover_text)
	system.nav.closeParentWindow(event)
	return


def btn_paper_change(event):
	rc = event.source.parent
	note = "{notes}".format(notes=rc.getComponent('txtFldNotesField').text)
	changeover_level = 1
	changeover_text = "Paper Change"
	changeoverCodeID = 8
	commit_event(rc.downtimeID,changeoverCodeID,"AutoChangeoverPopupSubmit",note,changeover_text)
	system.nav.closeParentWindow(event)
	return


def tbl_changeover_configureCell(self, value, textValue, selected, rowIndex, colIndex, colName, rowView, colView):
	if colIndex > 0 and self.parent.selectedCells.getValueAt(rowIndex,colIndex):
		return {'background': 'yellow'}
	elif rowView % 2 == 0:
		return {'background': '#D0D8e8'}
	else:
		return {'background': 'e9edf4'}


def tbl_changeover_codes_blown(self,value,textValue,selected,rowIndex,colIndex,colName,rowView,colView):

	blown_data = {
		0: { # Changeover Level 1
			0: "<html><br>CO1<br><br>" # Code
			,1: "<html>Below 10"  # Size
			,2: "<html>Below 1 mil"  # Gauge
			,3: ""  # Wind
			,4: ""  # Resins
			,5: ""  # Color
			,6: ""  # Barrier
			,7: ""  # Purge
			,8: ""  # Seal
			,9: ""  # Equipment
			,10: ""  # MDO
			}
		,1: {  # Changeover Level 2
			0: "<html>CO2"  # Code
			,1: "<html>Above 10"  # Size
			,2: "<html>Above 1 mil"  # Gauge
			,3: "<html>Wind<br>Config<br>Change"  # Wind
			#,4: "<html><ul><li>Up to 2 Mains</li><li>Up to 4 Hoppers<li>Any Additive % Changes</li></ul>"  # Resins
			#,4: "<html>Up to 2 Mains<hr>Up to 4 Hoppers<hr>Any Additive % Changes"  # Resins
			,4: "<html>Up to 2 Mains<br>Up to 4 Hoppers<br>Any Additive % Changes"  # Resins
			,5: "<html>Into color"  # Color
			,6: ""  # Barrier
			,7: ""  # Purge
			,8: ""  # Seal
			,9: "<html>Into/Out of<br>Secondary Treaters<br>or Annealing"  # Equipment
			,10: ""  # MDO
		}
		,2: {  # Changeover Level 3
			0: "<html>CO3"  # Code
			,1: ""  # Size
			,2: ""  # Gauge
			,3: ""  # Wind
			,4: "<html>Up to 3 Mains<br>More Than 4 Hoppers"  # Resins
			,5: ""  # Color
			,6: "<html>Into Barrier<br>Single Layer"  # Barrier
			,7: ""  # Purge
			,8: ""  # Seal
			,9: "<html>Air Slitter<br>Blade Change<br>Into/Out of Venter<br>Planned Downtime"  # Equipment
			,10: '<html>2" or less<br>Stay in<br>PMDO Mode'  # MDO
		}
		,3: {  # Changeover Level 4
			0: "<html>CO4"  # Code
			,1: ""  # Size
			,2: ""  # Gauge
			,3: ""  # Wind
			,4: "<html>4 Or More Mains<br>8 or More Hoppers"  # Resins
			,5: "<html>Out of Color<br>Up To 3<br>Extruders"  # Color
			,6: "<html>Into Barrier<br>Multi-Layer"  # Barrier
			,7: "<html>1 Extruder<br>Non-Barrier"  # Purge
			,8: "<html>Bagger<br>Seal<br>Change"  # Seal
			,9: "<html>Into/Out of Printer<br>Lane Treat Setup<br>In/Out of Gussets<br>Vfolder or<br>CMD Adjustments"  # Equipment
			,10: '<html>Size Change<br>above 2" to 12"<br>Out of<br>PMDO Mode<br>Re-Dial In TD'  # MDO
		}
		,4: {  # Changeover Level 5
			0: "<html>CO5"  # Code
			,1: ""  # Size
			,2: ""  # Gauge
			,3: ""  # Wind
			,4: ""  # Resins
			,5: "<html>Out of Color<br>More Than 3<br>Extruders"  # Color
			,6: "<html>Out of<br>Barrier<br>Single layer"  # Barrier
			,7: "<html>2 or More<br>Extruders<br>Non-Barrier"  # Purge
			,8: ""  # Seal
			,9: "<html>Equipment Changes<br>With or Without<br>Line Downtime"  # Equipment
			,10: '<html>Above 12"<br>Out of<br>PMDO Mode<br>All Blend<br>Changes'  # MDO
		}
		,5: {  # Changeover Level 6
			0: "<html>CO6"  # Code
			,1: ""  # Size
			,2: ""  # Gauge
			,3: ""  # Wind
			,4: "<html>Purge Bio Material<br>Any Extruder"  # Resins
			,5: ""  # Color
			,6: "<html>Out of Barrier<br>Multi-Layer"  # Barrier
			,7: ""  # Purge
			,8: ""  # Seal
			,9: "<html>Line Overhaul<br>Non-Routine<br>Equipment Changes<br>Full Line Cleaning"  # Equipment
			,10: "<html>Into/Out of<br>MDO<br>Purge In/Out<br>MDO Cleaning"  # MDO
		}
	}

	if colIndex > 0 and self.parent.selectedCells.getValueAt(rowIndex,colIndex):
		background = "yellow"
	elif rowView % 2 == 0:
		background = "#D0D8e8"
	else:
		background = "e9edf4"

	columnNames = ["Code","Size","Gauge","Wind","Resins","Color","Barrier","Purge","Seal","Equip","MDO"]
	columnWidths = [75,	185,	185,	125,	250,	175,	  175,	 150,	100,	250,	200]
	defaultColumnWidth = 100
	if rowIndex == 0:
		if colIndex < len(columnWidths):
			# Set the columns to a fixed size as they are painted
			self.table.columnModel.getColumn(colIndex).minWidth = columnWidths[colIndex]
			self.table.columnModel.getColumn(colIndex).maxWidth = columnWidths[colIndex]
			self.table.columnModel.getColumn(colIndex).width = columnWidths[colIndex]
		else:
			# Set any columns not specified to a default width
			self.table.columnModel.getColumn(colIndex).minWidth = defaultColumnWidth
			self.table.columnModel.getColumn(colIndex).maxWidth = defaultColumnWidth
			self.table.columnModel.getColumn(colIndex).width = defaultColumnWidth
	config_data = {
		"background": background
		,"text": blown_data[rowIndex][colIndex]
	}


	return config_data


def tbl_changeover_configureHeaderStyle(self, colIndex, colName):
	from javax.swing import SwingConstants
	return {
		'foreground': 'white',
		'background': '79,129,189',
		'horizontalAlignment': SwingConstants.CENTER}


def tbl_changeover_onMouseClick(self, rowIndex, colIndex, colName, value, event):
	if colIndex > 0:
		if len(value) > 0:
			cells_used = [ idx for idx in range(self.data.rowCount) if self.data.getValueAt(idx, colIndex) != "" ]
			selectedCells =  self.parent.selectedCells
			currentValue = selectedCells.getValueAt(rowIndex, colIndex)
			newValue = not currentValue
			for rowID in cells_used:
				if currentValue:
					selectedCells = system.dataset.setValue(selectedCells, rowID, colIndex, False)
				else:
					if rowID == rowIndex:
						selectedCells = system.dataset.setValue(selectedCells, rowID, colIndex, newValue)
					else:
						selectedCells = system.dataset.setValue(selectedCells, rowID, colIndex, currentValue)
			self.parent.selectedCells = selectedCells
		getChangeoverLevel(event)
		system.db.refresh(self,"data")
	return