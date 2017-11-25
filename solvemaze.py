import hashlib
sha256 = lambda s: hashlib.sha256(path).digest()

import amaze

amaze.makeMaze()

path = ''

pos = (amaze.size-2,amaze.size-2,amaze.size-2)
level = amaze.getM(pos)

while pos != (1,1,1):
	found = False
	for i in range(len(amaze.directions)):
		d = amaze.directions[i]
		if amaze.getM(d(pos)) == level-1:
			path += str(i)
			pos = d(d(pos))
			level -= 1
			found = True
			break
	if not found:
		raise Exception()

print path
print amaze.testPath(path)

h = sha256(sha256(path))

url = 'http://gbhfpixmagkbskmo.onion/'

print [ord(h[i]) ^ ord(url[i]) for i in range(len(url))]

