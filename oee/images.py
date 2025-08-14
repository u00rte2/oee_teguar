
def getImageFromFile():
	image_bytes = None
	path = system.file.openFile()
	if path is not None:
		image_bytes = system.file.readFileAsBytes(path)
	return image_bytes


def getImageFromGlass(itemCode):
	import system
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


#################################


def repaint(event):
	# itemCode = "CNG_Logo"
	# itemCode = "Pet_Food"
	# Add custom property: usePetFood then bind to check box
	if event.source.parent.getComponent('chkPetFood').selected:
		itemCode = "Pet_Food"
	else:
		itemCode = "CNG_Logo"


	g = event.graphics
	cachedName = event.source.getClientProperty("img-bytes-cached-name")

	# bytes = event.source.getClientProperty("img-bytes-cached")
	# if itemCode!=cachedName or not bytes:
	#	print "Image not cached - load from database"
	#	bytes = getImageFromGlass(itemCode)
	#	event.source.putClientProperty("img-bytes-cached",bytes)
	#	event.source.putClientProperty("img-bytes-cached-name",itemCode)

	bytes = getImageFromGlass(itemCode)[0][0]

	if bytes:
		from javax.imageio import ImageIO
		from java.io import ByteArrayInputStream

		#	from java.awt.geom import AffineTransform
		#	scale = AffineTransform()
		image = ImageIO.read(ByteArrayInputStream(bytes))

		g.drawImage(image,0,0,event.width,event.height,event.source)















if __name__ == "__main__":
	main()



