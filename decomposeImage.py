import sys

from PIL import Image, ImageMath



shift = 64

def morph(image, shift):
	xSize, ySize = image.size
	pixels = image.load()
	for y in range(ySize):
		rowShift = y * shift
		row = [pixels[x,y] for x in range(xSize)]
		for x in range(xSize):
			pixels[x,y] = row[(x+rowShift) % xSize]


inImageFile = sys.argv[-1]

image = Image.open(inImageFile)
xSize, ySize = image.size
print 'Image size: ', image.size

redImage, greenImage, blueImage = list(image.split())

redImage   = ImageMath.eval('a & 0x01', a=redImage)
greenImage = ImageMath.eval('a & 0x01', a=greenImage)
blueImage   = ImageMath.eval('a & 0x01', a=blueImage)

redImage = ImageMath.eval('(a^b)*128', a=redImage, b=greenImage)
morph(redImage, -shift)
redImage.show()


