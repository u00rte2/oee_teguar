def annotateTimestamp(event):
	from org.jfree.chart.annotations import XYTextAnnotation
	from java.awt import Color
	chartComponent = event.source.parent.getComponent('Status Chart')
	data = chartComponent.data
	chart = chartComponent.chart
	plot = chart.XYPlot
	for annotation in plot.getAnnotations():
		if isinstance(annotation, XYTextAnnotation):
			plot.removeAnnotation(annotation)
	def format_time(timestamp):
		days = int(timestamp / 86400)
		hours = int((timestamp % 86400) / 3600)
		minutes = int((timestamp % 3600) / 60)
		seconds = int(timestamp % 60)
		output = []
		if days > 0:
			output.append(str(days) + 'd')
		if hours > 0:
			output.append(str(hours) + 'h')
		if minutes > 0:
			output.append(str(minutes) + 'm')
		if seconds > 0:
			output.append(str(seconds) + 's')
		return ' : '.join(output) if output else '0s'
	def generateLabel(series, item, lastItemIndex):
		x = series - 1
		startDate = data.getValueAt(lastItemIndex, 0).getTime()
		endDate = data.getValueAt(item, 0).getTime()
		y = (float(startDate) + float(endDate)) * 0.5
		timeDiff = format_time((float(endDate) - float(startDate)) / 1000) #Time diff is being calculated here, but this could be literally anything
		annotation = XYTextAnnotation(timeDiff, x, y) #Timediff string added to chart
		annotation.setPaint(Color.BLACK)
		annotation.setFont(chartComponent.rangeAxisFont)
		plot.addAnnotation(annotation)
	for series in range(1, data.columnCount):
		lastItemValue = data.getValueAt(0, series)
		nextItemValue = data.getValueAt(1, series)
		lastItemIndex = 0
		for item in range(1, data.rowCount):
			if lastItemValue != nextItemValue:
				generateLabel(series, item, lastItemIndex)
				if (item + 1) < data.rowCount:
					lastItemValue = nextItemValue
					nextItemValue = data.getValueAt(item + 1, series)
					lastItemIndex = item
				else:
					generateLabel(series, item, lastItemIndex)
			else:
				if (item + 1) < data.rowCount:
					nextItemValue = data.getValueAt(item + 1, series)
				else:
					generateLabel(series, item, lastItemIndex)
	return