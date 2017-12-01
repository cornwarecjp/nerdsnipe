import hashlib
import struct

inputData = '\xfe'*32 #256-bit input data
expectedOutputData = hashlib.sha256(inputData).digest()



def rightrotate(x, amount):
	lowerBits = x >> amount
	higherBits = (x << (32 - amount)) & 0xffffffff
	return higherBits | lowerBits




#Note 1: All variables are 32 bit unsigned integers and addition is calculated modulo 232
#Note 2: For each round, there is one round constant k[i] and one entry in the message schedule array w[i], 0 <= i <= 63
#Note 3: The compression function uses 8 working variables, a through h
#Note 4: Big-endian convention is used when expressing the constants in this pseudocode,
#    and when parsing message block data from bytes to words, for example,
#    the first word of the input message "abc" after padding is 0x61626380

#Initialize hash values:
#(first 32 bits of the fractional parts of the square roots of the first 8 primes 2..19):
h0 = 0x6a09e667
h1 = 0xbb67ae85
h2 = 0x3c6ef372
h3 = 0xa54ff53a
h4 = 0x510e527f
h5 = 0x9b05688c
h6 = 0x1f83d9ab
h7 = 0x5be0cd19

#Initialize array of round constants:
#(first 32 bits of the fractional parts of the cube roots of the first 64 primes 2..311):
k = \
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
w = []
for i in range(16):
	w.append(struct.unpack('>I', inputData[4*i:4*(i+1)])[0])

#Extend the first 16 words into the remaining 48 words w[16..63] of the message schedule array:
for i in range(16,64):
	s0 = rightrotate(w[i-15], 7) ^ rightrotate(w[i-15], 18) ^ (w[i-15] >> 3)
	s1 = rightrotate(w[i-2], 17) ^ rightrotate(w[i-2], 19) ^ (w[i-2] >> 10)
	w.append((w[i-16] + s0 + w[i-7] + s1) & 0xffffffff)

#Initialize working variables to current hash value:
a = h0
b = h1
c = h2
d = h3
e = h4
f = h5
g = h6
h = h7

#Compression function main loop:
for i in range(64):
	S1 = rightrotate(e, 6) ^ rightrotate(e, 11) ^ rightrotate(e, 25)
	ch = (e & f) ^ ((~e) & g)
	temp1 = (h + S1 + ch + k[i] + w[i]) & 0xffffffff
	S0 = rightrotate(a, 2) ^ rightrotate(a, 13) ^ rightrotate(a, 22)
	maj = (a & b) ^ (a & c) ^ (b & c)
	temp2 = (S0 + maj) & 0xffffffff

	h = g
	g = f
	f = e
	e = (d + temp1) & 0xffffffff
	d = c
	c = b
	b = a
	a = (temp1 + temp2) & 0xffffffff

#Add the compressed chunk to the current hash value:
h0 = (h0 + a) & 0xffffffff
h1 = (h1 + b) & 0xffffffff
h2 = (h2 + c) & 0xffffffff
h3 = (h3 + d) & 0xffffffff
h4 = (h4 + e) & 0xffffffff
h5 = (h5 + f) & 0xffffffff
h6 = (h6 + g) & 0xffffffff
h7 = (h7 + h) & 0xffffffff

#Produce the final hash value (big-endian):
digest = ''
for h in (h0,h1,h2,h3,h4,h5,h6,h7):
	digest += struct.pack('>I', h)

print 'Expected: ', expectedOutputData.encode('hex')
print 'Actual:   ', digest.encode('hex')

