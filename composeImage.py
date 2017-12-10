import sys
from itertools import izip

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



inImageFile, outImageFile, greenDataFile, redImageFile, blueDataFile = sys.argv[1:]

image = Image.open(inImageFile)
xSize, ySize = image.size
print 'Image size: ', image.size


def binDataToImage(data):
	data = [bin(ord(byte))[2:] for byte in data]
	data = ['0'*(8-len(byte)) + byte for byte in data]
	data = ''.join(data)

	if len(data) > xSize*ySize:
		raise Exception('Image too small for data file')
	print 'Data: %d %% coverage' % (100*len(data)/(xSize*ySize))

	data = data * (1 + xSize*ySize/len(data))
	data = data[:(xSize*ySize)]
	return Image.frombytes('L', image.size, data)


def loadGreenImage():
	with open(greenDataFile, 'rb') as f:
		greenData = f.read()
	greenData = "You're on to something:\0" + greenData
	return binDataToImage(greenData)

greenImage = loadGreenImage()
greenImage = ImageMath.eval('a & 0x01', a=greenImage)

redImage = Image.open(redImageFile)
if redImage.size != image.size:
	raise Exception('Red image has wrong size')
redImage = redImage.convert(mode='L')
morph(redImage, shift)
redImage = ImageMath.eval('(a/128)^b', a=redImage, b=greenImage)

def loadBlueImage():
	with open(blueDataFile, 'rb') as f:
		blueData = f.read()
	return binDataToImage(blueData)

blueImage = loadBlueImage()
blueImage = ImageMath.eval('(a & 0x01)^b', a=blueImage, b=greenImage)

imageMode = image.mode
image = list(image.split())

image[0] = ImageMath.eval('convert((a & 0xfe) | b, "L")', a=image[0], b=redImage)
image[1] = ImageMath.eval('convert((a & 0xfe) | b, "L")', a=image[1], b=greenImage)
image[2] = ImageMath.eval('convert((a & 0xfe) | b, "L")', a=image[2], b=blueImage)

image = Image.merge(imageMode, image)

image.save(outImageFile)


redImage = ImageMath.eval('(a^b)*128', a=redImage, b=greenImage)
morph(redImage, -shift)
redImage.show()

blueImage = ImageMath.eval('(a^b)*128', a=blueImage, b=greenImage)
morph(blueImage, -2*shift)
blueImage.show()

