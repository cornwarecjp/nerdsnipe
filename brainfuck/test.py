import sys



maxMemory = 30000
maxProgram = 1000000
maxInstructions = 200000



inputData = raw_input('Input: ')


progFile = sys.argv[1]
with open(progFile, 'rb') as f:
	program = f.read()
if len(program) > maxProgram:
	raise Exception('Maximum program size exceeded')
maxProgram = len(program)
progPtr = 0


jumpTable = {}
def fillJumpTable():
	stack = []
	for p1 in range(maxProgram):
		if program[p1] == '[':
			stack.append(p1)
		elif program[p1] == ']':
			if len(stack) == 0:
				raise Exception('Program malformed: ] found without matching [')
			p2 = stack.pop(-1)
			jumpTable[p1] = p2
			jumpTable[p2] = p1
	if len(stack) != 0:
		raise Exception('Program malformed: [ found without matching ]')
fillJumpTable()


memory = [0]*maxMemory
memPtr = 0


def incrementMemPtr():
	global memPtr
	memPtr = (memPtr+1) % maxMemory


def decrementMemPtr():
	global memPtr
	memPtr = (memPtr-1) % maxMemory


def incrementValue():
	memory[memPtr] = (memory[memPtr]+1) % 256


def decrementValue():
	memory[memPtr] = (memory[memPtr]-1) % 256


def writeOutput():
	print '%02x' % memory[memPtr],
	#sys.stdout.write(chr(memory[memPtr]))


def readInput():
	global inputData
	if len(inputData) == 0:
		raise Exception('Read past end of input')
	memory[memPtr] = ord(inputData[0])
	inputData = inputData[1:]


def loopStart():
	global progPtr
	if memory[memPtr] == 0:
		progPtr = jumpTable[progPtr]


def loopEnd():
	global progPtr
	if memory[memPtr] != 0:
		progPtr = jumpTable[progPtr]


instructionTable = \
{
'>': incrementMemPtr,
'<': decrementMemPtr,
'+': incrementValue,
'-': decrementValue,
'.': writeOutput,
',': readInput,
'[': loopStart,
']': loopEnd
}


intructionCounter = 0
while progPtr < maxProgram:
	try:
		function = instructionTable[program[progPtr]]
	except KeyError:
		pass
	else:
		function()

	progPtr += 1
	intructionCounter += 1
	if intructionCounter > maxInstructions:
		raise Exception('Execution takes too long: maximum number of instructions exceeded')

