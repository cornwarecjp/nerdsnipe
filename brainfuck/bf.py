from collections import defaultdict
import sys
from collections import deque


maxMemory = 30000
maxProgram = 1000000
maxInstructions = 1000000000



inputData = ''
memory = [0]*maxMemory
pointers = [0,0] #progPtr, memPtr


class changeValueFunction:
	def __init__(self, increment):
		self.increment = increment

	def __call__(self):
		#print 'changeValue', increment
		memory[pointers[1]] = (memory[pointers[1]] + self.increment) % 256

	def getCode(self):
		return 'memory[i] += %d;\n' % self.increment


class changePointerFunction:
	def __init__(self, increment):
		self.increment = increment

	def __call__(self):
		#print 'changepointer', increment
		pointers[1] = (pointers[1] + self.increment) % maxMemory

	def getCode(self):
		increment = self.increment % maxMemory
		return 'i = (i + %d) %% MAXMEM;\n' % increment


class writeOutputFunction:
	def __call__(self):
		#print '%02x' % memory[pointers[1]],
		sys.stdout.write(chr(memory[pointers[1]]))

	def getCode(self):
		return 'putchar(memory[i]);\n'


class readInputFunction:
	def __call__(self):
		global inputData
		if len(inputData) == 0:
			raise Exception('Read past end of input')
		memory[pointers[1]] = ord(inputData[0])
		inputData = inputData[1:]

	def getCode(self):
		return 'memory[i] = getchar();\n'


class jumpForwardFunction:
	def __init__(self, p):
		self.p = p

	def __call__(self):
		#print 'jumpForward to', p
		if memory[pointers[1]] == 0:
			pointers[0] = self.p

	def getCode(self):
		return 'while(memory[i]) {\n'


class jumpBackwardFunction:
	def __init__(self, p):
		self.p = p

	def __call__(self):
		#print 'jumpForward to', p
		if memory[pointers[1]] != 0:
			pointers[0] = self.p

	def getCode(self):
		return '}\n'


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

	def getCode(self):
		ret = ''
		for offset, multiplier in self.increments.iteritems():
			offset = offset % maxMemory
			ret += 'memory[(i + %d) %% MAXMEM] += %d * memory[i]; ' % (offset, multiplier)
		ret += 'memory[i] = 0;\n'
		return ret



def convertToFunctions(program):
	program = deque(program)
	newProgram = []
	while program:
		#print len(program), len(newProgram)
		c = program.popleft()

		if c in '+-':
			increment = 1 if c=='+' else -1
			while program and program[0] in '+-':
				c = program.popleft()
				increment += 1 if c=='+' else -1
			newProgram.append(changeValueFunction(increment))

		elif c in '<>':
			increment = 1 if c=='>' else -1
			while program and program[0] in '<>':
				c = program.popleft()
				increment += 1 if c=='>' else -1
			newProgram.append(changePointerFunction(increment))

		elif c in '[]':
			newProgram.append(c)

		elif c == '.':
			newProgram.append(writeOutputFunction())

		elif c == ',':
			newProgram.append(readInputFunction())

	return newProgram


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


def determineJumps():
	stack = []
	for p1 in range(len(program)):
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


def run():
	intructionCounter = 0
	while pointers[0] < len(program):
		program[pointers[0]]()
		pointers[0] += 1
		intructionCounter += 1
		if intructionCounter > maxInstructions:
			sys.exit(1)


def compileCode():
	ret = \
'''
#include <stdio.h>
#include <stdlib.h>

#define MAXMEM %d
unsigned char memory[MAXMEM];
unsigned int i = 0;

#define MAXINSTRCOUNT %d
void incrementInstrCount()
{
	static unsigned int count = 0;
	count++;
	if(count > MAXINSTRCOUNT) exit(1);
}

int main(int argc, char **argv)
{
''' % (maxMemory, maxInstructions)

	for p in program:
		ret += '	incrementInstrCount(); '
		ret += p.getCode()

	ret += \
'''
return 0;
}
'''
	return ret


doCompile = '--compile' in sys.argv
if doCompile:
	progFile = sys.argv[-2]
	tgtFile  = sys.argv[-1]
else:
	progFile = sys.argv[-1]

with open(progFile, 'rb') as f:
	program = f.read()
if len(program) > maxProgram:
	raise Exception('Maximum program size exceeded')
program = list(program)
program = convertToFunctions(program)
program = detectValueMoves(program)
determineJumps()
if doCompile:
	code = compileCode()
	with open(tgtFile, 'wb') as f:
		f.write(code)
else:
	inputData = raw_input()
	run()

	if '--debug' in sys.argv:
		print
		print "MEMORY POINTER: ", pointers[1]
		print "MEMORY DUMP:"
		for i in range(1024):
			print '%02x' % memory[i],
			if (i+1) % 32 == 0:
				print

