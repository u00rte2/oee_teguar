def btnAcknowledgeAlarms(event):
	def getBody():
		html_body = """<html>
								<head>
									<style>table {{font-family: arial, sans-serif;border-collapse: collapse;width: 100%;}}
										td,
											th {{border: 1px solid #dddddd;text-align: left;padding: 8px;}}
											tr:nth-child(even) {{background-color: #dddddd;}}</style>
								</head>
								Venture Deviation Alarms have been acknowledged for Line {lineNumber}.<br>
								The current job number is: {orderNumber}<br>
								The current product is: {productCode}<br>
								<br>
								Acked by: {ackedBy}<br>
								Approved by: {approvedBy}<br>
								Notes: {note}<br>
								<br>
								The following alarms were acknowledged:<br>
								<table>
									<tr><th>Alarm</th>
										<th>Material</th>
										<th>Desired Setpoint</th>
										<th>Event Value</th>
										<th>Current Value</th>
										<th>Low Limit</th>
										<th>High Limit</th>
									</tr>
							""".format(lineNumber=rc.lineNumber,
									   orderNumber=initialValues["orderNumber"],
									   productCode=initialValues["productCode"],
									   ackedBy=rc.operator,
									   approvedBy=rc.approvedBy,
									   note=rc.notes
									   )
		return html_body

	def append_body(params):
		html = """
		<tr><td>{label}</td>
			<td>{material}</td>
			<td>{setpoint}</td>
			<td>{eventValue}</td>
			<td>{currentValue}</td>
			<td>{lowLimit}</td>
			<td>{hiLimit}</td>
		""".format(**params)

		return html

	def getPaths(alarm_name, alm_source):
		alarmPath = ":/alm:{alarm_name}".format(alarm_name=alarm_name)
		alm_source = alm_source.replace('prov:','[').replace(':/tag:',']').replace(alarmPath,'')
		base_path = alm_source[ :alm_source.rfind('/') + 1 ]
		labelPath = alm_source + "/Alarms/{}.Label".format(alarm_name)
		alarmPaths = {
			"label": labelPath,
			"material": base_path + "Material",
			"eventValue": labelPath.replace("Label", "EventValue"),
			"currentValue": alm_source
		}
		if alarm_name == "Deviation from Venture Setpoint":
			alarmPaths["lowLimit"] = base_path + "Venture Deviation Lower Setpoint"
			alarmPaths["hiLimit"] = base_path + "Venture Deviation Upper Setpoint"
		elif alarm_name == "Layer Thickness Deviation":
			alarmPaths["setpoint"] = base_path + "Venture Layer Thickness Setpoint"
		elif alarm_name == "Venture Thickness Deviation":
			alarmPaths["setpoint"] = base_path + "Venture Thickness Setpoint"
		elif alarm_name == "Density Deviation":
			alarmPaths["setpoint"] = base_path + "Venture Density Setpoint"
		return alarmPaths

	def readBlocking(kwargs):
		data = { }
		data.clear()
		tag_names = kwargs.keys()
		tag_paths = [ kwargs[ tag_name ] for tag_name in tag_names ]
		objs = system.tag.readBlocking(tag_paths)
		for tag_key,obj in zip(tag_names,objs):
			data[ tag_key ] = obj.value
		return data

	rc = event.source.parent
	# Run acknowledge alarm script
	alarms = rc.alarms
	# create base path for tags
	provider = "[{}]".format(rc.provider)
	initialPaths = {
		"orderNumber": "{provider}Line{lineNumber}/Order/Order Number".format(provider=provider, lineNumber=rc.lineNumber),
		"productCode": "{provider}Line{lineNumber}/Product/Product".format(provider=provider, lineNumber=rc.lineNumber),
		"densityTolerance": "{provider}OT/Density Deviation Tolerance".format(provider=provider)
		# "recipients": "{provider}OT/Deviation Acknowledge Recipients".format(provider=provider)
	}
	recipients = "zach.merrilees@cnginc.com"
	# read blocking for initial values
	initialValues = readBlocking(initialPaths)
	body = getBody()
	eventIDs = [ ]
	# set html values based on alarm tags, differs from alarm to alarm
	for i in range(alarms.rowCount):
		eventIDs.append( alarms.getValueAt(i,'eventId') )
		almSource = alarms.getValueAt(i,'source')
		if ":/alm:Deviation from Venture Setpoint" in almSource:
			alarmName = "Deviation from Venture Setpoint"
			paths = getPaths(alarmName,almSource)
			values = readBlocking(paths)
			html_params = {"label": values["label"],
						"material": values["material"],
						"setpoint": round((values["lowLimit"] + values["hiLimit"]) / 2, 2),
						"eventValue": round(values["eventValue"], 2),
						"currentValue": values["currentValue"],
						"lowLimit": round(values["lowLimit"], 2),
						"hiLimit": round(values["hiLimit"], 2)
			}
			body += append_body(html_params)
		elif "':/alm:Layer Thickness Deviation' "in almSource:
			alarmName = "Layer Thickness Deviation"
			paths = getPaths(alarmName,almSource)
			values = readBlocking(paths)
			html_params = {"label": values["label"],
						"material": values["material"],
						"setpoint": round(values["setpoint"], 3),
						"eventValue": round(values["eventValue"], 3),
						"currentValue": values["currentValue"],
						"lowLimit": round(values["setpoint"] - (values["setpoint"] * .05), 3),
						"hiLimit": round(values["setpoint"] + (values["setpoint"] * .05), 3)
			}
			body += append_body(html_params)
		elif ':/alm:Venture Thickness Deviation' in almSource:
			alarmName = "Venture Thickness Deviation"
			paths = getPaths(alarmName,almSource)
			values = readBlocking(paths)
			html_params = {"label": values["label"],
						"material": "",
						"setpoint": round(values["setpoint"], 3),
						"eventValue": round(values["eventValue"], 3),
						"currentValue": values["currentValue"],
						"lowLimit": round(values["setpoint"] - (values["setpoint"] * .03), 3),
						"hiLimit": round(values["setpoint"] + (values["setpoint"] * .03), 3)
			}
			body += append_body(html_params)
		elif ':/alm:Missing Material' in almSource:
			alarmName = "Missing Material"
			paths = getPaths(alarmName,almSource)
			values = readBlocking(paths)
			html_params = {"label": values["label"],
						"material": values[ "currentValue" ],
						"setpoint": "",
						"eventValue": "",
						"currentValue": "",
						"lowLimit": "",
						"hiLimit": ""
			}
			body += append_body(html_params)
		elif ':/alm:Density Deviation' in almSource:
			alarmName = "Density Deviation"
			paths = getPaths(alarmName,almSource)
			values = readBlocking(paths)
			html_params = {"label": values["label"],
						"material": values["material"],
						"setpoint": round(values[ "eventValue" ], 3),
						"eventValue": round(values[ "eventValue" ], 3),
						"currentValue": values[ "currentValue" ],
						"lowLimit": round(set - (values["setpoint"] * initialValues["densityTolerance"] / 100),3),
						"hiLimit": round(set + (values["setpoint"] * initialValues["densityTolerance"] / 100),3)
			}
			body += append_body(html_params)
		else:
			alarmName = "Extra Materials"
			paths = getPaths(alarmName,almSource)
			values = readBlocking(paths)
			html_params = {"label": values["label"],
						"material": values["currentValue"],
						"setpoint": "",
						"eventValue": "",
						"currentValue": "",
						"lowLimit": "",
						"hiLimit": ""
			}
			body += append_body(html_params)
	# acknowledge alarm, send email, and close popup
	notesFinal = "Acked by: {ackedBy}, Approved by: {approvedBy}, Notes: {notes}".format(ackedBy=rc.operator,approvedBy=rc.approvedBy,notes=rc.notes)
	ack = system.alarm.acknowledge(eventIDs, notesFinal)
	system.net.sendEmail(smtp = 'mail.charternex.com',
						 fromAddr = 'ignition@cnginc.com',
						 subject = 'Venture Deviation Alarm(s) Acknowledged',
						 body = body,
						 #to = [ row[ "emailAddress" ] for row in system.dataset.toPyDataSet(initialValues[ "recipients" ]) ],
						 to=[ recipients ],
						 smtpProfile = 'CharterNEX Email')
	system.nav.closeWindow("Alarms/AcknowledgePopup")
	return