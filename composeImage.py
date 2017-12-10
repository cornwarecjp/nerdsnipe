import sys
from itertools import izip

from PIL import Image, ImageMath
import qrcode



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

def loadGreenImage():
	with open(greenDataFile, 'rb') as f:
		greenData = f.read()

	greenData = "You're on to something:\0" + greenData

	#lsb = [ord(c) & 0x0f for c in greenData]
	#msb = [(ord(c) & 0xf0) >> 4 for c in greenData]
	#greenData = ''.join([chr(c) for pair in izip(lsb,msb) for c in pair])

	greenData = [bin(ord(byte))[2:] for byte in greenData]
	greenData = ['0'*(8-len(byte)) + byte for byte in greenData]
	greenData = ''.join(greenData)

	if len(greenData) > xSize*ySize:
		raise Exception('Image too small for green data file')
	print 'Green data: %d %% coverage' % (100*len(greenData)/(xSize*ySize))

	greenData = greenData * (1 + xSize*ySize/len(greenData))
	greenData = greenData[:(xSize*ySize)]
	return Image.frombytes('L', image.size, greenData)
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

	qr = qrcode.QRCode(
		box_size=1,
		border=0,
	)
	qr.add_data(blueData)

	qr.make(fit=True)
	qr = qr.make_image()

	ret = Image.new('L', size=image.size, color=255)
	topleft = ((ret.size[0]-qr.size[0])/2, (ret.size[1]-qr.size[1])/2)
	if topleft[0] < 0 or topleft[1] < 0:
		raise Exception('QR code does not fit')
	ret.paste(qr, topleft)
	return ret

blueImage = loadBlueImage()
morph(blueImage, 2*shift)
blueImage = ImageMath.eval('(a/128)^b', a=blueImage, b=greenImage)

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

