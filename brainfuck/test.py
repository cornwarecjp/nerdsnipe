from collections import defaultdict
import sys
import hashlib



maxMemory = 30000
maxProgram = 1000000
maxInstructions = 1000000000



inputData = '\xfe'*32 #256-bit input data
expectedOutputData = hashlib.sha256(inputData).digest()

memory = [0]*maxMemory
pointers = [0,0] #progPtr, memPtr


class changeValueFunction:
	def __init__(self, increment):
		self.increment = increment

	def __call__(self):
		#print 'changeValue', increment
		memory[pointers[1]] = (memory[pointers[1]] + self.increment) % 256


class changePointerFunction:
	def __init__(self, increment):
		self.increment = increment

	def __call__(self):
		#print 'changepointer', increment
		pointers[1] = (pointers[1] + self.increment) % maxMemory


def writeOutputFunction():
	def f():
		print '%02x' % memory[pointers[1]],
		#sys.stdout.write(chr(memory[pointers[1]]))
	return f


def readInputFunction():
	def f():
		global inputData
		if len(inputData) == 0:
			raise Exception('Read past end of input')
		memory[pointers[1]] = ord(inputData[0])
		inputData = inputData[1:]
	return f


def jumpForwardFunction(p):
	def f():
		#print 'jumpForward to', p
		if memory[pointers[1]] == 0:
			pointers[0] = p
	return f

def jumpBackwardFunction(p):
	def f():
		#print 'jumpForward to', p
		if memory[pointers[1]] != 0:
			pointers[0] = p
	return f


class moveValueFunction:
	def __init__(self, increments):
		self.increments = increments

	def __call__(self):
		sourceValue = memory[pointers[1]]
		memory[pointers[1]] = 0
		for offset, multiplier in self.increments.iteritems():
			address = (pointers[1] + offset) % maxMemory
			increment = multiplier * sourceValue
			memory[address] = (memory[address] + increment) % 256


#Load file
progFile = sys.argv[1]
with open(progFile, 'rb') as f:
	program = f.read()
if len(program) > maxProgram:
	raise Exception('Maximum program size exceeded')
program = list(program)


def convertToFunctions(program):
	newProgram = []
	while program:
		c = program.pop(0)

		if c in '+-':
			increment = 1 if c=='+' else -1
			while program and program[0] in '+-':
				c = program.pop(0)
				increment += 1 if c=='+' else -1
			newProgram.append(changeValueFunction(increment))

		elif c in '<>':
			increment = 1 if c=='>' else -1
			while program and program[0] in '<>':
				c = program.pop(0)
				increment += 1 if c=='>' else -1
			newProgram.append(changePointerFunction(increment))

		elif c in '[]':
			newProgram.append(c)

		elif c == '.':
			newProgram.append(writeOutputFunction())

		elif c == ',':
			newProgram.append(readInputFunction())

	return newProgram
program = convertToFunctions(program)


def detectValueMoves(program):
	newProgram = []

	while program:
		c = program.pop(0)

		if c != '[':
			newProgram.append(c)
			continue

		codeInLoop = []
		isValueMove = False
		while True:
			c = program.pop(0)
			if isinstance(c, changeValueFunction) or isinstance(c, changePointerFunction):
				codeInLoop.append(c)
			elif c == ']':
				isValueMove = True
				break
			elif c == '[':
				newProgram += ['['] + codeInLoop
				codeInLoop = []
			else:
				newProgram += ['['] + codeInLoop + [c]
				codeInLoop = []
				isValueMove = False
				break

		if not isValueMove:
			continue

		increments = defaultdict(lambda: 0)
		offset = 0
		for c in codeInLoop:
			if isinstance(c, changePointerFunction):
				offset += c.increment
			elif isinstance(c, changeValueFunction):
				increments[offset] += c.increment

		if offset != 0 or increments[0] != -1:
			#It's not a value move after all
			newProgram += ['['] + codeInLoop + [']']
			continue

		del increments[0]
		newProgram.append(moveValueFunction(increments))

	return newProgram
program = detectValueMoves(program)


maxProgram = len(program)


def determineJumps():
	stack = []
	for p1 in range(maxProgram):
		if program[p1] == '[':
			stack.append(p1)
		elif program[p1] == ']':
			if len(stack) == 0:
				raise Exception('Program malformed: ] found without matching [')
			p2 = stack.pop(-1)
			program[p1] = jumpBackwardFunction(p2)
			program[p2] = jumpForwardFunction(p1)

	if len(stack) != 0:
		raise Exception('Program malformed: [ found without matching ]')
determineJumps()

intructionCounter = 0
while pointers[0] < maxProgram:
	program[pointers[0]]()
	pointers[0] += 1
	intructionCounter += 1
	if intructionCounter > maxInstructions:
		raise Exception('Execution takes too long: maximum number of instructions exceeded')


print
print "MEMORY DUMP:"
for i in range(1024):
	print '%02x' % memory[i],
	if (i+1) % 32 == 0:
		print

