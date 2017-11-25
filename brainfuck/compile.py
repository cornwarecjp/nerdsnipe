import cProfile
import sys



isFinishedCode = lambda s: len([c for c in s if c not in '<>+-[]!?~']) == 0



class CodeBlock:
	def __init__(self, code):
		self.code = code[:]


	def evaluateMacros(self):
		macros = {}
		oldCode = self.code
		newCode = []

		while True:
			try:
				e = oldCode.pop(0)
			except IndexError:
				break

			if e != '{':
				newCode.append(e)
				continue
			#We found a code open

			macroCode = []
			openCount = 1
			while True:
				try:
					e = oldCode.pop(0)
				except IndexError:
					raise Exception('{ not matched with }')

				if e == '{':
					openCount += 1
				elif e == '}':
					openCount -= 1
					if openCount == 0:
						break

				macroCode.append(e)

			if newCode.pop(-1) != ')':
				raise Exception('Expected ) before {')

			arguments = ''
			while True:
				try:
					e = newCode.pop(-1)
				except IndexError:
					raise Exception('( before { not found')

				if e == '(':
					break

				arguments = e + arguments
			arguments = arguments.split(';')

			name = newCode.pop(-1)

			#print 'EXTRACTED MACRO ', name
			#print '    MACRO ARGUMENTS: ', arguments
			#print '    MACRO CODE: ', macroCode

			macros[name] = Macro(macroCode, arguments)

		self.code = newCode

		#print 'CODE WITHOUT MACROS(1) ', self.code

		while True:
			newCode = self.evaluate(macros)
			if newCode == self.code:
				break
			self.code = newCode

		#print 'CODE WITHOUT MACROS(2) ', self.code


	def evaluate(self, namespace):
		code = self.code[:]
		newCode = []

		#print 'EVALUATE ', code
		#print '    NAMESPACE ', namespace.keys()

		def appendToList(newCode, l):
			#print '    APPEND ', newCode, l
			#Merge finished code at start and end:
			if len(newCode)>0 and len(l)>0 and isFinishedCode(newCode[-1]) and isFinishedCode(l[0]):
				newCode[-1] += l[0]
				newCode += l[1:]
			else:
				#Add to newCode
				newCode += l
			#print '         = ', newCode

		while len(code) > 0:
			symbol = code.pop(0)
			if symbol not in namespace:
				appendToList(newCode, [symbol])
				continue

			obj = namespace[symbol]

			#print 'CODE: ', code

			if isinstance(obj, Macro):
				#print '    Expanding macro ', symbol

				if code.pop(0) != '(':
					raise Exception('( in macro invocation not found')

				argumentValues = [[]]
				openCount = 1
				while len(code) > 0:
					symbol = code.pop(0)
					#print '    PROCESSING', symbol, openCount

					if symbol == ')' and openCount == 1:
						openCount = 0
						break
					if symbol == ';' and openCount == 1:
						argumentValues.append([])
						continue

					argumentValues[-1].append(symbol)

					if symbol == '(':
						openCount += 1
					elif symbol == ')':
						openCount -= 1

				if openCount != 0:
					raise Exception(') in macro invocation not found')

				argumentValues = \
				[
				CodeBlock(a).evaluate(namespace)
				for a in argumentValues
				]

				macroCode = obj.evaluate(argumentValues)
				appendToList(newCode, macroCode)

			elif isinstance(obj, list):
				#print '    Substituting symbol ', symbol, '=', obj
				appendToList(newCode, obj)

			else:
				raise Exception('Unknown object type')

		return newCode



class Macro:
	def __init__(self, code, arguments):
		self.codeBlock = CodeBlock(code)
		self.codeBlock.evaluateMacros()
		self.arguments = arguments


	def evaluate(self, argumentValues):
		#print 'EVALUATING MACRO'
		#print 'CODE:', self.codeBlock.code
		#print 'ARGUMENTS:', self.arguments
		#print 'ARGUMENTVALUES:', argumentValues
		namespace = {self.arguments[i]:argumentValues[i] for i in range(len(self.arguments))}
		return self.codeBlock.evaluate(namespace)



readFile, writeFile = sys.argv[1:]

with open(readFile, 'rb') as f:
	code = f.read()

code = code.split('\n')
for i in range(len(code)):
	#Remove comment
	pos = code[i].find('#')
	if pos >= 0:
		code[i] = code[i][:pos]
	#strip
	code[i] = code[i].strip()
code = ' '.join(code)

#Uniform spacing:
code = code.replace('\t', ' ')
for c in '{}();':
	code = code.replace(c, ' ' + c + ' ')
while True:
	newCode = code.replace('  ', ' ')
	if newCode == code:
		break
	code = newCode
code = code.split(' ')

#print code

codeBlock = CodeBlock(code)
#codeBlock.evaluateMacros()
cProfile.run('codeBlock.evaluateMacros()')
code = codeBlock.evaluate({})
code = ''.join(code)

#print code

#Evaluate save-and-recall:
stack = []
currentPos = 0
newCode = ''
for c in code:
	if c == '!':
		stack.append(currentPos)
		currentPos = 0
		continue
	elif c == '?':
		newCode += '<'*currentPos if currentPos>0 else '>'*-currentPos
		currentPos = 0
		continue
	elif c == '~':
		currentPos = stack.pop(-1)
		continue

	newCode += c
	if c == '>':
		currentPos += 1
	elif c == '<':
		currentPos -= 1
code = newCode

#Remove non-code:
code = ''.join([c for c in code if c in '<>+-.,[]'])

#Optimize:
while True:
	newCode = code
	newCode = newCode.replace('><', '')
	newCode = newCode.replace('<>', '')
	newCode = newCode.replace('+-', '')
	newCode = newCode.replace('-+', '')
	if newCode == code:
		break
	code = newCode

with open(writeFile, 'wb') as f:
	f.write(code)

