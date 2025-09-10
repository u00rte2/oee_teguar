from javax.imageio import ImageIO
from java.io import ByteArrayInputStream

def getImageFromFile():
	image_bytes = None
	path = system.file.openFile()
	if path is not None:
		image_bytes = system.file.readFileAsBytes(path)
	return image_bytes


def getImageFromDatabase(itemCode):
#	import system
	database = "Glass"
	qry = "SELECT imageBlob FROM soc.images WHERE itemCode = '{}'".format(itemCode)
	image_bytes = system.db.runQuery(qry, database)
	return image_bytes



def saveImage(image_bytes):
	database = "Glass"
	system.db.runPrepUpdate("INSERT INTO soc.images (imageBlob) VALUES (?)", [image_bytes])
	return


def main():
	image_bytes = getImageFromFile()
	saveImage(image_bytes)
	return


def repaint(event):
	# itemCode = "CNG_Logo"
	# itemCode = "Pet_Food"
	# Add custom property: usePetFood then bind to check box
	#print 'repaint'
	if event.source.trigger:
		itemCode = "Pet_Food"
	else:
		itemCode = "CNG_Logo"
	g = event.graphics
	cachedName = event.source.getClientProperty("image_bytes_cached_name")
	image_bytes = event.source.getClientProperty("image_bytes_cached")
	if itemCode != cachedName or not image_bytes:
		print "Image not cached - load from database"
		image_bytes = getImageFromDatabase(itemCode)[0][0]
		event.source.putClientProperty("image_bytes_cached",image_bytes)
		event.source.putClientProperty("image_bytes_cached_name",itemCode)

	# image_bytes = getImageFromDatabase(itemCode)[0][0]
	if image_bytes:
		#	from java.awt.geom import AffineTransform
		#	scale = AffineTransform()
		image = ImageIO.read(ByteArrayInputStream(image_bytes))
		g.drawImage(image,0,0,event.width,event.height,event.source)