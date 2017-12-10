import sys

import qrcode


def getPixel(image, y, x):
	res = image.getpixel((x,y))
	return res != 0


def makeQR(text):
	qr = qrcode.QRCode(
		box_size=1,
		border=1,
	)
	qr.add_data(text)

	qr.make(fit=True)
	qr = qr.make_image()

	#qr.show()

	S = qr.size[0]/2

	text = ''
	for y in range(S):
		line = ''
		for x in range(S):
			for h in range(2):
				pxbot = getPixel(qr, 2*y  , 2*x+h)
				pxtop = getPixel(qr, 2*y+1, 2*x+h)
				c = \
				{
				(0,0): chr(219), #'B',
				(0,1): chr(223), #'p',
				(1,0): chr(220), #'b',
				(1,1): ' '
				}[(pxbot, pxtop)]
				line += c
		text += line + '\r\n'

	return text



inFile, outFile = sys.argv[1:]
with open(inFile, 'rb') as f:
	text = f.read()

text = makeQR(text)

with open(outFile, 'wb') as f:
	f.write(text)

