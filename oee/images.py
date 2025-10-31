from javax.imageio import ImageIO
from java.io import ByteArrayInputStream

def getImageFromFile():
	image_bytes = None
	path = system.file.openFile()
	if path is not None:
		image_bytes = system.file.readFileAsBytes(path)
	return image_bytes


def getImageFromGlass(itemCode):
	database = "glass"
	qry = "SELECT imageBlob FROM soc.images WHERE itemCode = '{}'".format(itemCode)
	image_bytes = system.db.runQuery(qry, database)
	# print "image retrieved from Glass", type(image_bytes[0][0])
	return image_bytes


def getImageFromSnowFlake(itemCode):
	database = "SnowFlake"
	qry = "EXEC [OT].[SharePointImage_Get] N'{}'".format(itemCode)
	image_bytes = system.db.runQuery(qry, database)
	# print "image retrieved from SnowFlake",type(image_bytes[0][0])
	return image_bytes


def saveImage(itemCode, image_bytes):
	database = "glass"
	system.db.runPrepUpdate("INSERT INTO soc.images (itemCode, imageBlob) VALUES (?,?)", [itemCode, image_bytes], database)
	return


def repaint(event):
	itemCode =  event.source.itemCode
	g = event.graphics
	cachedName = event.source.getClientProperty("image_bytes_cached_name")
	image_bytes = event.source.getClientProperty("image_bytes_cached")
	if itemCode != cachedName or not image_bytes:
		# print "{} Image not cached - load from database".format(itemCode)
		image_bytes = getImageFromSnowFlake(itemCode)[0][0]
		if image_bytes is None:
			image_bytes = getImageFromGlass("CNG_Logo")[0][0]
		event.source.putClientProperty("image_bytes_cached",image_bytes)
		event.source.putClientProperty("image_bytes_cached_name",itemCode)
	if image_bytes:
		#from java.awt.geom import AffineTransform
		#scale = AffineTransform()
		image = ImageIO.read(ByteArrayInputStream(image_bytes))
		g.drawImage(image,0,0,event.width,event.height,event.source)


def load_cng_logo(event):
	"""
	The cng logo provided by snowflake is a crappy image.
	Load a copy of thier image for future reference.
	If they return this image again then replace it with ours.
	:return:
	"""
	rc = system.gui.getParentWindow(event).getRootContainer()
	image_bytes = getImageFromGlass("snowflake_logo")[0][0]
	image_finder = rc.getComponent("cntHeader").getComponent("image_finder")
	image_finder.source.putClientProperty("image_bytes_crappy_logo", image_bytes)
	return