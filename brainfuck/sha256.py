import hashlib
import struct

inputData = '\xfe'*32 #256-bit input data
expectedOutputData = hashlib.sha256(inputData).digest()



def rightrotate(x, amount):
	lowerBits = x >> amount
	higherBits = (x << (32 - amount)) & 0xffffffff
	return higherBits | lowerBits



class Memory:
	def __init__(self):
		#Initialize hash values:
		#(first 32 bits of the fractional parts of the square roots of the first 8 primes 2..19):
		self.h0 = 0x6a09e667
		self.h1 = 0xbb67ae85
		self.h2 = 0x3c6ef372
		self.h3 = 0xa54ff53a
		self.h4 = 0x510e527f
		self.h5 = 0x9b05688c
		self.h6 = 0x1f83d9ab
		self.h7 = 0x5be0cd19

		self.s0 = 0
		self.s1 = 0
		self.ch = 0
		self.maj = 0
		self.temp1 = 0
		self.temp2 = 0

		self.a = 0
		self.b = 0
		self.c = 0
		self.d = 0
		self.e = 0
		self.f = 0
		self.g = 0
		self.h = 0

		self.w = [0]*64

		#Initialize array of round constants:
		#(first 32 bits of the fractional parts of the cube roots of the first 64 primes 2..311):
		self.k = \
		[
		   0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
		   0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
		   0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
		   0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
		   0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
		   0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
		   0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
		   0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
		]


	def dump(self):
		'''
		0x00 h0
		0x04 h1
		0x08 h2
		0x0c h3
		0x10 h4
		0x14 h5
		0x18 h6
		0x1c h7

		0x20 s0
		0x24 s1
		0x28 ch
		0x2c maj
		0x30 temp1
		0x34 temp2
		0x38 a
		0x3c b

		0x40 c
		0x44 d
		0x48 e
		0x4c f
		0x50 g
		0x54 h
		0x58 stack0
		0x5c stack1

		0x60 stack2
		0x64 stack3
		0x68 stack4
		0x6c stack5
		0x70 stack6
		0x74 A.space
		0x75 A.i1
		0x76 A.i2
		0x77 A.data
		0x7b w[0]

		0x17b k[0]
		'''

		ret = ''
		for h in [self.h0, self.h1, self.h2, self.h3, self.h4, self.h5, self.h6, self.h7]:
			ret += struct.pack('>I', h)

		ret += struct.pack('>I', self.s0)
		ret += struct.pack('>I', self.s1)
		ret += struct.pack('>I', self.ch)
		ret += struct.pack('>I', self.maj)
		ret += struct.pack('>I', self.temp1)
		ret += struct.pack('>I', self.temp2)

		ret += struct.pack('>I', self.a)
		ret += struct.pack('>I', self.b)
		ret += struct.pack('>I', self.c)
		ret += struct.pack('>I', self.d)
		ret += struct.pack('>I', self.e)
		ret += struct.pack('>I', self.f)
		ret += struct.pack('>I', self.g)
		ret += struct.pack('>I', self.h)

		#Stack
		ret += struct.pack('>I', 0)
		ret += struct.pack('>I', 0)
		ret += struct.pack('>I', 0)
		ret += struct.pack('>I', 0)
		ret += struct.pack('>I', 0)
		ret += struct.pack('>I', 0)
		ret += struct.pack('>I', 0)

		#Array
		ret += struct.pack('B', 0) #A.space
		ret += struct.pack('B', 0) #A.i1
		ret += struct.pack('B', 0) #A.i2
		ret += struct.pack('>I', 0)#A.data

		for w in self.w:
			ret += struct.pack('>I', w)
		for k in self.k:
			ret += struct.pack('>I', k)

		return ret



mem = Memory()

#Note 1: All variables are 32 bit unsigned integers and addition is calculated modulo 232
#Note 2: For each round, there is one round constant k[i] and one entry in the message schedule array w[i], 0 <= i <= 63
#Note 3: The compression function uses 8 working variables, a through h
#Note 4: Big-endian convention is used when expressing the constants in this pseudocode,
#    and when parsing message block data from bytes to words, for example,
#    the first word of the input message "abc" after padding is 0x61626380


#Pre-processing:
#begin with the original message of length L bits
#append a single '1' bit
#append K '0' bits, where K is the minimum number >= 0 such that L + 1 + K + 64 is a multiple of 512
#append L as a 64-bit big-endian integer, making the total post-processed length a multiple of 512 bits
inputData += '\x80' + '\x00'*(64 - len(inputData) - 8 - 1) + '\x00\x00\x00\x00\x00\x00\x01\x00'

#Process the message in successive 512-bit chunks:
#break message into 512-bit chunks
#for each chunk

#create a 64-entry message schedule array w[0..63] of 32-bit words
#(The initial values in w[0..63] don't matter, so many implementations zero them here)
#copy chunk into first 16 words w[0..15] of the message schedule array
for i in range(16):
	mem.w[i] = struct.unpack('>I', inputData[4*i:4*(i+1)])[0]

#Extend the first 16 words into the remaining 48 words w[16..63] of the message schedule array:
for i in range(16,64):
	mem.s0 = rightrotate(mem.w[i-15], 7) ^ rightrotate(mem.w[i-15], 18) ^ (mem.w[i-15] >> 3)
	mem.s1 = rightrotate(mem.w[i-2], 17) ^ rightrotate(mem.w[i-2], 19) ^ (mem.w[i-2] >> 10)
	mem.w[i] = (mem.w[i-16] + mem.s0 + mem.w[i-7] + mem.s1) & 0xffffffff

#Initialize working variables to current hash value:
mem.a = mem.h0
mem.b = mem.h1
mem.c = mem.h2
mem.d = mem.h3
mem.e = mem.h4
mem.f = mem.h5
mem.g = mem.h6
mem.h = mem.h7

#Compression function main loop:
for i in range(64):
	mem.s1 = rightrotate(mem.e, 6) ^ rightrotate(mem.e, 11) ^ rightrotate(mem.e, 25)
	mem.ch = (mem.e & mem.f) ^ ((~mem.e) & mem.g)
	mem.temp1 = (mem.h + mem.s1 + mem.ch + mem.k[i] + mem.w[i]) & 0xffffffff
	mem.s0 = rightrotate(mem.a, 2) ^ rightrotate(mem.a, 13) ^ rightrotate(mem.a, 22)
	mem.maj = (mem.a & mem.b) ^ (mem.a & mem.c) ^ (mem.b & mem.c)
	mem.temp2 = (mem.s0 + mem.maj) & 0xffffffff

	mem.h = mem.g
	mem.g = mem.f
	mem.f = mem.e
	mem.e = (mem.d + mem.temp1) & 0xffffffff
	mem.d = mem.c
	mem.c = mem.b
	mem.b = mem.a
	mem.a = (mem.temp1 + mem.temp2) & 0xffffffff

#Add the compressed chunk to the current hash value:
mem.h0 = (mem.h0 + mem.a) & 0xffffffff
mem.h1 = (mem.h1 + mem.b) & 0xffffffff
mem.h2 = (mem.h2 + mem.c) & 0xffffffff
mem.h3 = (mem.h3 + mem.d) & 0xffffffff
mem.h4 = (mem.h4 + mem.e) & 0xffffffff
mem.h5 = (mem.h5 + mem.f) & 0xffffffff
mem.h6 = (mem.h6 + mem.g) & 0xffffffff
mem.h7 = (mem.h7 + mem.h) & 0xffffffff

#Produce the final hash value (big-endian):
digest = ''
for h in (mem.h0,mem.h1,mem.h2,mem.h3,mem.h4,mem.h5,mem.h6,mem.h7):
	digest += struct.pack('>I', h)

print 'Expected: ', expectedOutputData.encode('hex')
print 'Actual:   ', digest.encode('hex')

print
print 'MEMORY DUMP:'
dump = mem.dump()
for i in range(len(dump)):
	print '%02x' % ord(dump[i]),
	if (i+1) % 32 == 0:
		print

