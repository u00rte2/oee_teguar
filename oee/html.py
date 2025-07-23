def getHeader(database, socID):
	""" Returns a single row dataset of header information with the following columns:
			socID
			sourceID
			plantID
			lineLinkID
			lineNumber
			plantName
			lineName
			lineCode
			productCode
			itemCode
			itemMasterID
			dtrStation
			socCreationDate
			socCaptureDate
			socReviewer
			socComments
			targetWidth
			targetMil
			deleteFlag
			socRevLevel
			socRevisionDate
			socRevisedBy
			socRevisionComments

		Parameters:
			database, string: (glass points to dev and glass_cnfsql04 points to live data)
			socID, int:
	"""
	qry = "EXEC [soc].[getSOCHeaderRevInfoBySocV5_SP] @socID=%d" % (socID)
	dsHeader = system.db.runQuery(qry,database)
	return dsHeader


def getData(database, socID):
	""" Returns a dataset of data (multiple rows)for an soc with the following columns:
			pk_socID
			plantName
			lineName
			lineCode
			SectionName
			ColumnName
			RowName
			value
			sourceID
			plantID
			lineLinkID
			lineNumber
			tagOrder
		Parameters:
			database, string: (glass points to dev and glass_cnfsql04 points to live data)
			socID, int
	"""
	qry = "EXEC [dtr].[getDataV5_SP] @socID=%d" % socID
	dsData = system.db.runQuery(qry,database)
	return dsData


def filterDataset(dataset, filterColumn, filterValue):
	""" Filters dataset and returns data for a given section (or table)
		Parameters:
			dataset, dataset: all data values for an soc
			filterColumn, string: column to search in
			filterValue, string: value to filter for
	"""
	rowsToDelete = []
	for idx in range(dataset.getRowCount()):
		if dataset.getValueAt(idx,filterColumn) != filterValue:
			rowsToDelete.append(idx)
	dsFiltered = system.dataset.deleteRows(dataset,rowsToDelete)
	return dsFiltered

def defineCSS():
	css = """
		<head>
			<style>
				.socTitle {
						font-family: Arial, Helvetica, sans-serif;
						font-size: 35pt;
						font-weight: bold;
						line-height: 10px;
						text-align: center;
						width: auto;
						margin-bottom: 3px;
						}
				.commentTable {
					border: 3px solid grey;
					border-collapse: collapse;
					grid-column-start: 1;
					grid-column-end: 7;
					grid-row: 5;
					}
				.socCommentTitle {
									font-family: monospace;
									font-size: 12pt;
									font-weight: bolder;
									text-align: center;
									}
				.socComment {
							font-family: Arial, Helvetica, sans-serif;
							font-size: 10pt;
							float:left;
							}
				.erpnote {
						background-color: Cyan;
						font-family: Arial, Helvetica, sans-serif;
						font-size: 10pt;
						line-height: 10px;
						text-align: center;
						width: auto;
						margin-top: 10px;
						margin-bottom: 3px;
						}
				.erpdata {
						background-color:Cyan
						}
				.linecode {
						font-family: Arial, Helvetica, sans-serif;
						font-size: 24pt;
						font-weight: bolder;
						line-height: 10px;
						text-align: left;
						width: auto;
						margin-bottom: 3px;
						}
				.socHeader {
						font-family: monospace;
						font-size: 10pt;
						display: flex;
						}
				#headeronly td:first-child{
											font-weight: bolder;
											text-align: right;
											}
				.headerTables {
								margin: 1rem;
								}
				.soc {
						font-family: monospace;
						font-size: 10pt;
						display: grid;
						grid-template-columns: repeat(6, 1fr);
						gap: 10px;
						grid-template-rows: 1in, repeat(5, 1fr);
					}
				.socfirstcolumn {
									font-weight: bolder;
									text-align: left;
									}
				.soctable {
						border: 3px solid grey;
						border-collapse: collapse;
						white-space: nowrap;
						height: 80%;
						}
				.rows {
						border: 1px solid;
						border-collapse: collapse;
						text-align: center;
						vertical-align: middle;
						padding: 1.5pt;
						}
				.headerrows {
						border: 1px solid;
						border-collapse: collapse;
						text-align: left;
						vertical-align: middle;
						padding: 1.5pt;
						}
				.soccaption {
							font-size: 12pt;
							font-weight: bold;
						}
				#socMain {
						grid-column-start: 1;
						grid-column-end: 3;
						grid-row: 2;
						text-align: left;
						}
				#socWinder {
						grid-column-start: 3;
						grid-column-end: 5;
						grid-row: 2;
						}
				table[id="socUser Defined"] {
											grid-column-start: 5;
											grid-column-end: 7;
											grid-row: 2;
										}
				#socAnnealing {
							grid-column-start: 3;
							grid-column-end: 5;
							grid-row: 3;
						}
				#socBubble {
							grid-column-start: 1;
							grid-column-end: 3;
							grid-row: 3;
						}
				table[id="socScreen Pack"] {
											grid-column-start: 5;
											grid-column-end: 7;
											grid-row: 3;
										}
				table[id="socDie Temps"] {
										grid-column-start: 1;
										grid-column-end: 2;
										grid-row: 4;
										}
				#socExtruder {
							grid-column-start: 2;
							grid-column-end: 7;
							grid-row: 4;
							}
				table[id="socMDO Main"] {
										grid-column-start: 1;
										grid-column-end: 4;
										grid-row: 5;
										}
				table[id="socMDO Other"] {
										grid-column-start: 4;
										grid-column-end: 5;
										grid-row: 5;
										}
			</style>
		</head>\n"""
	return css


def tab(level):
	tabs = "\t" * level
	return tabs


def createHTML_Open():
	html = "<!DOCTYPE html>\n"
	html += "<html>\n"
	return html


def createHTML_Close():
	html = tab(2) + "</body>\n"
	html += tab(1) + "</html>"
	return html


def createTitle(header):
	# Main Title
	lineCode = header[0]["plantCode2"] + "-L"+ str(header[0]["lineNumber"])
	html = tab(2) + "<body>\n"
	html += tab(3) + """<div class="socTitle">\n"""
	html += tab(4) + "<p>Standard Operating Conditions</p>\n"
	html += tab(3) + "</div>\n"
	# ERP Note
	html += tab(3) + """<div>\n"""
	html += tab(4) + """<p><span class="erpnote">(From ERP)</span></p>\n"""
	html += tab(3) + "</div>\n"
	# Line Code
	html += tab(3) + """<div>\n"""
	html += tab(4) + """<p><span class="linecode">%s</span></p>\n""" % lineCode
	html += tab(3) + "</div>\n"
	return html


def createHTMLheader(headerData, socData):

	def getColumnNames(tableNumber):
		# For reference only
		sp_columnNames = [
						"socID",
						"sourceID",
						"plantID",
						"lineLinkID",
						"lineNumber",
						"plantCode2",
						"productCode",
						"itemCode",
						"itemMasterID",
						"dtrStation",
						"socCreationDate",
						"socCaptureDate",
						"socOriginalOrderNumber",
						"socReviewer",
						"socComments",
						"targetWidth",
						"targetMil",
						"deleteFlag",
						"socRevLevel",
						"socRevisionDate",
						"socRevisionCaptureDate",
						"socRevisionOrderNumber",
						"socRevisedBy",
						"socRevisionComments"
						]
		tbl1_ColumnNames = [
						"socID",
						"dtrStation",
						"socReviewer",
						"socCreationDate",
						"socCaptureDate"
						]
		tbl1_cleanColumnNames = [
							"SOC:",
							"Station:",
							"Revised By:",
							"Created:",
							"Captured:"
							]
		tbl2_ColumnNames = [
						"productCode",
						"itemCode",
						"targetWidth",
						"targetMil"
						]
		tbl2_cleanColumnNames = [
							"Product Code:",
							"Item Code:",
							"Width:",
							"Mil:"
							]
		tbl3_ColumnNames = [
						"socRevLevel",
						"socRevisionDate",
						"socRevisionComments"
						]
		tbl3_cleanColumnNames = [
							"Rev Level:",
							"Revision Date:",
							"Revision Comments:"
							]
		if tableNumber == 1:
			return tbl1_ColumnNames, tbl1_cleanColumnNames
		if tableNumber == 2:
			return tbl2_ColumnNames, tbl2_cleanColumnNames
		if tableNumber == 3:
			return tbl3_ColumnNames, tbl3_cleanColumnNames
		return None

	def getMachineValue(socData, rowName):
		machineValue = ""
		for row in socData:
			if row["SectionName"] == "main" and row["RowName"] == rowName:
				rawValue = row["value"]
				machineValue = str(rawValue)
		return machineValue

	def getTableHTML(tableNumber, headerData, socData):
		openTable = tab(5) + """<table class="headerTables">\n""" + tab(6) + """<tbody class="headerrows">\n"""
		closeTable = tab(6) + "</tbody>\n" + tab(4) +"</table>\n"
		html = ""
		html += openTable
		columnNames, cleanColumnNames =  getColumnNames(tableNumber)
		if tableNumber in (1,3):
			for i, columnName in enumerate(columnNames):
				value = headerData[0][columnName]
				if str(value) == "nan":
					value = ""
				html += tab(7) + "<tr>\n" + \
				tab(8) + "<td>%s</td>\n" % cleanColumnNames[i] + \
				tab(8) + "<td>%s</td>\n" % str(value) + \
				tab(7) + "</tr>\n"
		if tableNumber == 2:
			for i, columnName in enumerate(columnNames):
				if columnName == "targetWidth":
					erpWidth = "(" + str(headerData[0][columnName]) + ")"
					machineWidth = getMachineValue(socData, "Width")
					html += tab(6) + "<tr>\n" + \
					tab(8) + """<td>%s</td>\n""" % cleanColumnNames[i] + \
					tab(8) + """<td>%s, <span class="erpdata">%s</span></td>\n""" % (machineWidth, erpWidth) + \
					tab(7) + "</tr>\n"
				elif columnName == "targetMil":
					erpMil = "(" + str(headerData[0][columnName]) + ")"
					machineMil = getMachineValue(socData, "Gauge")
					html += tab(6) + "<tr>\n" + \
					tab(8) + """<td>%s</td>\n""" % cleanColumnNames[i] + \
					tab(8) + """<td>%s, <span class="erpdata">%s</span></td>\n""" % (machineMil, erpMil) + \
					tab(7) + "</tr>\n"
				elif tableNumber == 2:
					erpValue = "(" + str(headerData[0][columnName]) + ")"
					html += tab(6) + "<tr>\n" + \
					tab(8) + "<td>%s</td>\n" % cleanColumnNames[i] + \
					tab(8) + """<td><span class="erpdata">%s</span></td>\n""" % erpValue + \
					tab(7) + "</tr>\n"
		return html + closeTable

	openHeader = tab(3) + """<div class="socHeader" id="headeronly">\n"""
	closeHeader = tab(3) + "</div>\n" + tab(1) + "</header>\n"
	headerhtml = openHeader
	for tableNumber in range(1, 4):
		headerhtml += getTableHTML(tableNumber, headerData, socData)
	headerhtml += closeHeader
	return headerhtml


def createTableHTML(tableData, tableName):
	htmlText= ""
	htmlText += tab(2) + """<table class="soctable" id="soc%s"><tr>\n""" % tableName
	htmlText += tab(3) + """<caption class="soccaption"><b>%s</b></caption>\n""" % tableName
	htmlText += tab(3) + """<thead class="rows">\n"""
	htmlText+= tab(4) + "<tr>\n"
	for columnHeader in tableData.columnNames:
		htmlText+= tab(5) + "<th>%s</th>\n" % columnHeader
	htmlText+= tab(4) + "</tr>\n"
	htmlText += tab(3) + """</thead>\n"""
	htmlText += tab(3) + """<tbody class="rows">\n"""

	def excludedItem(row):
		itemsExcluded = ["Width", "Gauge"]
		for item in itemsExcluded:
			if item in row:
				return True
		return False

	def getString(col):
		if col in (None, "None"):
			newString = ""
		else:
			newString = str(col)
		return newString

	for row in tableData:
		if not excludedItem(row):
			i = 0
			htmlText+= tab(4) + "<tr>"
			for col in row:
				if i == 0:
					htmlText += tab(5) + """<td class="socfirstcolumn">%s</td>""" % col
				else:
					htmlText += tab(5) + "<td>%s</td>" % getString(col)
				i += 1
			htmlText += tab(4) + "</tr>"
	htmlText += tab(3) + "</tbody>\n"
	htmlText += tab(2) + "</table>\n"
	return htmlText


def processSocData(socData):

	def assembleDataset(socData, tableName):
		""" Some tables have more than one colunm. Extract data from the master dataset and assemble it into a single table.
		"""
		columnList = list(set([row["ColumnName"] for row in system.dataset.toPyDataSet(socData) if row["SectionName"] == tableName]))
		columnList.sort()
		headers = ["Parameters"]
		for idx in range(len(columnList)):
			columnName = str(columnList[idx])
			if columnName == "Screen Pack":
				headers = ["Extruder"]
			if idx == 0:
				tableData = system.dataset.toDataSet(headers,[[row["rowName"]] for row in system.dataset.toPyDataSet(socData) if row["columnName"] == str(columnList[idx])])
			tableData = system.dataset.addColumn(tableData,[row["value"] for row in system.dataset.toPyDataSet(socData) if row["columnName"] == columnList[idx]],str(columnList[idx]),str)
		return system.dataset.toPyDataSet(tableData)

	tables = list(set([row["SectionName"] for row in system.dataset.toPyDataSet(socData)]))
	sumHTML = tab(1) + """<div class="soc">\n"""
	for tableName in tables:
		html = createTableHTML(assembleDataset(socData, tableName), tableName)
		if len(sumHTML) == 0:
			sumHTML = html
		else:
			sumHTML = sumHTML + "\n" + html
	sumHTML += "</div>\n"
	return sumHTML


def processSocComments(headerData):
	socComments = headerData[0]["socComments"]
	if socComments is None:
		socComments = "No comments exist for this SOC."
	else:
		if len(socComments) == 0:
			socComments = "No comments exist for this SOC."
	html = tab(1) + """<div class="soc">\n"""
	html += tab(2) + """<table class="commentTable">\n"""
	html += tab(3) + """<caption class="socCommentTitle">Comment</caption>\n"""
	html += tab(3) + "<thead>\n"
	html += tab(4) + """<tr class="socComment">\n"""
	html += tab(5) + "<th>%s</th>\n" % socComments
	html += tab(5) + "</th>\n"
	html += tab(4) + "</tr>\n"
	html += tab(3) + "</thead>\n"
	html += tab(2) + "</table>\n"
	html += tab(1) + "</div>\n"
	return html


def assembleHTML(headerData, socData):
	html = ""
	html += createHTML_Open()
	html += defineCSS()
	html += createTitle(headerData)
	html += createHTMLheader(headerData, socData)
	html += processSocData(socData)
	html += processSocComments(headerData)
	html += createHTML_Close()
	return html


def getHTML(database, socID):
	""" Called from the gui.
	"""
	dsHeader = getHeader(database, socID)
	final_html = ''
	if dsHeader.getRowCount() > 0:
		socID = dsHeader.getValueAt(0, "socID")
		deleteFlag = dsHeader.getValueAt(0, "deleteFlag")
		if not deleteFlag == 1:
			dsData = getData(database, socID)
			final_html = assembleHTML(dsHeader, dsData)
	return final_html
