import sys
from collections import deque

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


def getBytes(image):
	bits = deque(image.tobytes())
	bytes = deque()
	while bits:
		byte = 0
		try:
			for i in range(8):
				byte = 2*byte + ord(bits.popleft())
		except IndexError:
			break #bits is probably empty
		bytes.append(byte)
	bytes = ''.join([chr(b) for b in bytes])

	subset = ''
	while True:
		subset += bytes[0]
		bytes = bytes[1:]

		if len(subset) > 100 and bytes.startswith(subset):
			break

	return subset


inImageFile = sys.argv[-1]

image = Image.open(inImageFile)
xSize, ySize = image.size
print 'Image size: ', image.size

redImage, greenImage, blueImage = list(image.split())

redImage   = ImageMath.eval('convert(a & 0x01, "L")', a=redImage)
greenImage = ImageMath.eval('convert(a & 0x01, "L")', a=greenImage)
blueImage  = ImageMath.eval('convert(a & 0x01, "L")', a=blueImage)

redImage = ImageMath.eval('convert((a^b)*128, "L")', a=redImage, b=greenImage)
morph(redImage, -shift)
redImage.show()

blueImage = ImageMath.eval('convert(a^b, "L")', a=blueImage, b=greenImage)
translation = \
{
chr(219): 'B',
chr(220): 'b',
chr(223): 'p'
}
print ''.join([
c if c not in translation else translation[c]
for c in getBytes(blueImage)
])

greenBytes = getBytes(greenImage)
pos = greenBytes.index('\0')
print greenBytes[:pos]
zipFile = greenBytes[pos+1:]
print len(zipFile)

