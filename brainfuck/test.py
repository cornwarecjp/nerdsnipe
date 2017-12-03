import sys
import hashlib
from random import SystemRandom
import os

rnd = SystemRandom()
inputData = ''.join([chr(rnd.randint(0,255)) for i in range(32)])
expectedOutputData = hashlib.sha256(inputData).digest()


with open('input.dat', 'wb') as f:
	f.write(inputData)

os.system(' '.join(sys.argv[1:]) + '< input.dat > output.dat')

with open('output.dat', 'rb') as f:
	actualOutputData = f.read()

print 'Input:           ', inputData.encode('hex')
print 'Expected output: ', expectedOutputData.encode('hex')
print 'Actual output  : ', actualOutputData.encode('hex')
print expectedOutputData == actualOutputData

