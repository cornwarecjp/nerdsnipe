import sys
import hashlib
from random import SystemRandom
import os

rnd = SystemRandom()
inputData = ''.join([chr(rnd.randint(0,255)) for i in range(32)])
expectedOutputData = hashlib.sha256(inputData).digest()


with open('tmp/input.dat', 'wb') as f:
	f.write(inputData)

exitCode = os.system(' '.join(sys.argv[1:]) + '< tmp/input.dat > tmp/output.dat')
if exitCode != 0:
	print 'Execution time exceeded'
	sys.exit(1)

with open('tmp/output.dat', 'rb') as f:
	actualOutputData = f.read()

print 'Input:           ', inputData.encode('hex')
print 'Expected output: ', expectedOutputData.encode('hex')
print 'Actual output  : ', actualOutputData.encode('hex')

if expectedOutputData != actualOutputData:
	sys.exit(1)

