import sys



class CodeBlock:
	def __init__(self, code):
		self.code = code[:]


	def evaluateMacros(self):
		macros = {}

		while True:
			#print 'CODE:', self.code

			try:
				codeStartPos = self.code.index('{')
			except ValueError:
				break
			openCount = 1
			codeEndPos = None
			for i in range(codeStartPos+1, len(self.code)):
				if self.code[i] == '{':
					openCount += 1
				elif self.code[i] == '}':
					openCount -= 1
					if openCount == 0:
						codeEndPos = i
						break
			if codeEndPos is None:
				raise Exception('{ not matched with }')

			if self.code[codeStartPos-1] != ')':
				raise Exception('Expected ) before {')

			argumentsStartPos = None
			i = codeStartPos-1
			while i > 1:
				i -= 1
				if self.code[i] == '(':
					argumentsStartPos = i
					break
			if argumentsStartPos is None:
				raise Exception('( before { not found')

			name = self.code[argumentsStartPos-1]
			arguments = self.code[argumentsStartPos+1:codeStartPos-1]
			arguments = ''.join(arguments)
			arguments = arguments.split(';')
			code = self.code[codeStartPos+1:codeEndPos]
			macros[name] = Macro(code, arguments)

			#print 'EXTRACTED MACRO ', name
			#print '    MACRO CODE: ', code

			self.code = self.code[:argumentsStartPos-1] + self.code[codeEndPos+1:]

		while True:
			newCode = self.evaluate(macros)
			if newCode == self.code:
				break
			self.code = newCode


	def evaluate(self, namespace):
		code = self.code[:]
		newCode = []

		while len(code) > 0:
			symbol = code.pop(0)
			if symbol not in namespace:
				newCode.append(symbol)
				continue

			obj = namespace[symbol]

			#print 'CODE: ', code

			if isinstance(obj, Macro):
				#print 'Expanding macro ', symbol

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
				newCode += macroCode

			elif isinstance(obj, list):
				newCode += obj

			else:
				raise Exception('Unknown object type')

		self.mergeCode(newCode)
		return newCode


	def mergeCode(self, code):
		isCode = lambda s: len([c for c in s if c not in '<>+-[]!?~']) == 0

		pos = 0
		while pos < len(code)-1:
			s1 = code[pos]
			if isCode(s1):
				s2 = code[pos+1]
				if isCode(s2):
					code[pos] = s1 + s2
					del code[pos+1]
					continue #continue without incrementing pos
			pos += 1


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

print code

codeBlock = CodeBlock(code)
codeBlock.evaluateMacros()
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

