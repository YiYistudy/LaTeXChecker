import os
from sys import argv, executable, exit
from re import findall
from time import sleep
PLATFORM = __import__("platform").system().upper()
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
CLEAR_SCREEN_COMMAND = ("CLS" if PLATFORM == "WINDOWS" else "clear") if __import__("sys").stdin.isatty() else None
STARTUP_COMMAND_FORMAT = "START \"\" \"{0}\" \"{1}\" \"{2}\"" if PLATFORM == "WINDOWS" else "\"{0}\" \"{1}\" \"{2}\"&"


class DebugLevel:
	defaultCharacter = "?"
	defaultName = "*"
	defaultSymbol = "[?]"
	defaultValue = 0
	def __init__(self:object, d:dict) -> object:
		self.character = d["character"] if "character" in d else DebugLevel.defaultCharacter
		self.name = d["name"] if "name" in d else DebugLevel.defaultName
		self.symbol = d["symbol"] if "symbol" in d else DebugLevel.defaultSymbol
		self.value = d["value"] if "value" in d else DebugLevel.defaultValue
	def __eq__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value == other.value
		elif isinstance(other, (int, float)):
			return self.value == other
		else:
			return False
	def __ne__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value != other.value
		elif isinstance(other, (int, float)):
			return self.value != other
		else:
			return True
	def __lt__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value < other.value
		elif isinstance(other, (int, float)):
			return self.value < other
		else:
			raise TypeError("TypeError: '<' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __le__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value <= other.value
		elif isinstance(other, (int, float)):
			return self.value <= other
		else:
			raise TypeError("TypeError: '<=' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __gt__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value > other.value
		elif isinstance(other, (int, float)):
			return self.value > other
		else:
			raise TypeError("TypeError: '>' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __ge__(self:object, other:object) -> bool:
		if isinstance(other, DebugLevel):
			return self.value >= other.value
		elif isinstance(other, (int, float)):
			return self.value >= other
		else:
			raise TypeError("TypeError: '>=' not supported between instances of '{0}' and '{1}'".format(type(self), type(other)))
	def __bool__(self:object) -> bool:
		return bool(self.value)
	def __int__(self:object) -> int:
		return self.value
	def __str__(self:object) -> str:
		return str(self.symbol)
Prompt = DebugLevel({"character":"P", "name":"Prompt", "symbol":"[P]", "value":100})
Fatal = DebugLevel({"character":"F", "name":"Fatal", "symbol":"[F]", "value":60})
Critical = DebugLevel({"character":"C", "name":"Critical", "symbol":"[C]", "value":50})
Error = DebugLevel({"character":"E", "name":"Error", "symbol":"[E]", "value":40})
Warning = DebugLevel({"character":"W", "name":"Warning", "symbol":"[W]", "value":30})
Info = DebugLevel({"character":"I", "name":"Info", "symbol":"[I]", "value":20})
Debug = DebugLevel({"character":"D", "name":"Debug", "symbol":"[D]", "value":10})

class PointerNode:
	def __init__(self:object, filePath:str, parentPointerNode:object = None) -> object:
		self.__filePath = os.path.abspath(str(filePath).replace("\"", "")) # must be an absolute path since __eq__ needs to use it
		self.__lineIdx = 0 # the initialization value
		self.__charIdx = -1 # the initialization value
		self.__parentPointerNode = parentPointerNode if isinstance(parentPointerNode, PointerNode) else None
		self.__children = None # initialization flag
		self.__lines = None # initialization flag
	def __getTxt(self:object, filePath:str, index:int = 0) -> str: # get .txt content
		coding = ("utf-8", "gbk", "utf-16") # codings
		if 0 <= index < len(coding): # in the range
			try:
				with open(filePath, "r", encoding = coding[index]) as f:
					content = f.read()
				return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
			except (UnicodeError, UnicodeDecodeError):
				return self.__getTxt(filePath, index + 1) # recursion
			except:
				return None
		else:
			return None # out of range
	def initialize(self:object) -> bool:
		content = self.__getTxt(self.__filePath)
		if content is None:
			self.__lines = None # avoid re-initialization
			self.__children = None # avoid re-initialization
			return False
		elif content:
			self.__lines = content.splitlines()
			self.__children = []
			return True
		else:
			self.__lines = [""]
			self.__children = []
			return True
	def isInitialized(self:object) -> bool:
		return isinstance(self.__lines, list) and isinstance(self.__children, list)
	def hasNextChar(self:object) -> bool: # only just the status of the current pointer node
		return 0 <= self.__lineIdx < len(self.__lines) and 0 <= self.__charIdx + 1 < len(self.__lines[self.__lineIdx]) if self.isInitialized() else None
	def nextChar(self:object) -> bool:
		bRet = self.hasNextChar() # judge if it is initialized and if there is a following character
		if bRet:
			self.__charIdx += 1 # increse the character count
		return bRet
	def hasNextLine(self:object) -> bool: # only just the status of the current pointer node
		return self.__lineIdx + 1 < len(self.__lines) if self.isInitialized() else None
	def nextLine(self:object) -> bool:
		bRet = self.hasNextLine() # judge if it is initialized and if there is a following line
		if bRet:
			self.__lineIdx += 1 # increase the line count
			self.__charIdx = -1 # reset the char index
		return bRet
	def isEOF(self:object) -> bool:
		return self.__lineIdx + 1 == len(self.__lines) and self.__charIdx >= 0 and self.__charIdx + 1 == len(self.__lines[self.__lineIdx]) if self.isInitialized() else None
	def getCurrentChar(self:object) -> str:
		return self.__lines[self.__lineIdx][self.__charIdx] if self.isInitialized() and self.__lineIdx < len(self.__lines) and 0 <= self.__charIdx < len(self.__lines[self.__lineIdx]) else None
	def getNextChar(self:object) -> str:
		return self.__lines[self.__lineIdx][self.__charIdx + 1] if self.hasNextChar() else None
	def getCurrentLine(self:object) -> str:
		return self.__lines[self.__lineIdx] if self.isInitialized() and self.__lineIdx < len(self.__lines) else None
	def getRemainingChars(self:object) -> str:
		return self.__lines[self.__lineIdx][self.__charIdx + 1:] if self.isInitialized() and self.__lineIdx < len(self.__lines) else None
	def addChildPointerNode(self:object, pointerNode:object) -> bool:
		if isinstance(pointerNode, PointerNode) and pointerNode.isInitialized():
			self.__children.append(pointerNode)
			return True
		else:
			return False
	def getFilePath(self:object) -> str:
		return self.__filePath if self.isInitialized() else None
	def getCurrentLocation(self:object) -> tuple:
		return (self.__filePath, self.__lineIdx, self.__charIdx)
	def getChildren(self:object, isReversed:bool = False) -> list:
		return (self.__children[::-1] if isReversed else self.__children[::]) if self.isInitialized() else None
	def __eq__(self:object, obj:str|object) -> bool:
		if PLATFORM == "WINDOWS":
			return isinstance(obj, PointerNode) and self.__filePath.lower() == obj.__filePath.lower() or isinstance(obj, str) and self.__filePath.lower() == obj.lower()
		else:
			return isinstance(obj, PointerNode) and self.__filePath == obj.__filePath or isinstance(obj, str) and self.__filePath == obj

class Pointer:
	def __init__(self:object, rootFilePath:str) -> object:
		absRootFilePath = os.path.abspath(str(rootFilePath).replace("\"", ""))
		self.__pointerNodeStack = [] # stack (stack[0] is the root) # initialization flag
		self.__pointerNodeStack.append(PointerNode(absRootFilePath)) # write separately to avoid the absence of this attribute caused by exceptions in PointerNode
		self.__currentPointerNode = None # initialization flag
		self.__baseFolderPath = os.path.split(absRootFilePath)[0]
		self.__lastError = "Currently, there are no errors. "
	def initialize(self:object) -> bool:
		if self.__pointerNodeStack and self.__pointerNodeStack[0].initialize():
			self.__currentPointerNode = self.__pointerNodeStack[0]
			return True
		else:
			self.__pointerNodeStack = [self.__pointerNodeStack[0]] if self.__pointerNodeStack else [] # avoid re-initialization
			self.__currentPointerNode = None # avoid re-initialization
			return False
	def isInitialized(self:object) -> bool:
		return bool(self.__pointerNodeStack) and isinstance(self.__currentPointerNode, PointerNode)
	def hasNextChar(self:object, fileSwitch:bool = True) -> bool: # in the current line including "1\input{2}3"
		if self.isInitialized():
			if self.__currentPointerNode.hasNextChar():
				return True
			elif isinstance(fileSwitch, bool) and fileSwitch:
				for i in range(len(self.__pointerNodeStack) - 1, -1, -1): # check the parents constantly
					if self.__pointerNodeStack[i].hasNextChar():
						return True
					elif not self.__pointerNodeStack[i].isEOF(): # there is a following line but there is not a following character
						return False
			return False # no following characters are followed / all the opened files report EOF
		else:
			return None # not initialized
	def nextChar(self:object, fileSwitch:bool = True) -> bool:
		bRet = self.hasNextChar(fileSwitch = fileSwitch) # judge if it is initialized and if there is a following character in the current line
		if bRet:
			while len(self.__pointerNodeStack) > 1: # no need to consider the switch again; keep the main file in the stack
				if self.__pointerNodeStack[-1].nextChar():
					return True
				elif not self.__pointerNodeStack[-1].isEOF(): # there is a following line but there is not a following character
					return False
				self.__pointerNodeStack.pop()
				self.__currentPointerNode = self.__pointerNodeStack[-1] # move the pointer
			if self.__pointerNodeStack[0].nextChar(): # all the opened non-main files report EOF
				return True
			else:
				return False # the main file
		else:
			return bRet
	def hasNextLine(self:object, fileSwitch:bool = True) -> bool:
		if self.isInitialized():
			if self.__currentPointerNode.hasNextLine():
				return True
			else:
				for i in range(len(self.__pointerNodeStack) - 1, -1, -1): # check the parents constantly
					if self.__pointerNodeStack[i].hasNextLine():
						return True
				return False # all the opened files report EOF
		else:
			return None # not initialized
	def nextLine(self:object, fileSwitch:bool = True) -> bool:
		bRet = self.hasNextLine() # judge if it is initialized and if there is a following line
		if bRet:
			while len(self.__pointerNodeStack) > 1: # keep the main file in the stack
				if self.__pointerNodeStack[-1].nextLine():
					return True
				self.__pointerNodeStack.pop()
				self.__currentPointerNode = self.__pointerNodeStack[-1] # move the pointer
			if self.__pointerNodeStack[0].nextLine(): # all the opened non-main files report the end of lines
				return True
			else:
				return False # the main file
		else:
			return bRet
	def getCurrentChar(self:object) -> str:
		return self.__currentPointerNode.getCurrentChar() if self.isInitialized() else None
	def getNextChar(self:object, fileSwitch:bool = True) -> str:
		bRet = self.hasNextChar(fileSwitch = fileSwitch) # judge if it is initialized and if there is a following character in the current line
		if bRet:
			for i in range(len(self.__pointerNodeStack) - 1, -1, -1): # check the parents constantly
					if self.__pointerNodeStack[i].hasNextChar():
						return self.__pointerNodeStack[i].getNextChar()
			return None # all the opened files report EOF
		else:
			return bRet
	def getCurrentLine(self:object) -> str:
		return self.__currentPointerNode.getCurrentLine() if self.isInitialized() else None
	def getRemainingCharactersInTheCurrentLineOfTheCurrentFile(self:object) -> str:
		return self.__currentPointerNode.getRemainingChars() if self.isInitialized() else None
	def getCurrentLocation(self:object) -> tuple:
		if self.isInitialized():
			tp = self.__currentPointerNode.getCurrentLocation()
			return (os.path.relpath(str(tp[0]), self.__baseFolderPath), tp[1], tp[2]) if isinstance(tp, tuple) else None
		else:
			return None
	def getCurrentLocationDescription(self:object) -> str:
		tp = self.getCurrentLocation()
		return ("Char {0}, Line {1}, File \"{2}\"".format(tp[2], tp[1] + 1, tp[0]) if tp[2] >= 0 else "Line {1}, File \"{2}\"".format(tp[2], tp[1] + 1, tp[0])) if isinstance(tp, tuple) else None
	def addPointerNode(self:object, filePath:str) -> bool:
		if not self.isInitialized():
			self.__lastError = "The instance of ``Pointer`` has not been initialized. "
			return False
		elif not isinstance(filePath, str):
			self.__lastError = "The passed file path is not a string. "
			return False
		strippedFilePath = filePath.replace("\"", "").strip()
		absFilePath = os.path.abspath(strippedFilePath if os.path.isabs(strippedFilePath) else os.path.join(self.__baseFolderPath, strippedFilePath))
		if absFilePath in self.__pointerNodeStack:
			self.__lastError = "The file \"{0}\" has been in the stack for resolving. Please check and make sure that there are no recursive calls. ".format(absFilePath).replace("\\", "\\\\")
			return False
		pointerNode = PointerNode(absFilePath, parentPointerNode = self.__currentPointerNode)
		if pointerNode.initialize() and self.__currentPointerNode.addChildPointerNode(pointerNode):
			self.__currentPointerNode = pointerNode
			self.__pointerNodeStack.append(pointerNode)
			return True
		else:
			self.__lastError = "Failed to initialize the call to \"{0}\". ".format(absFilePath).replace("\\", "\\\\")
			return False
	def getLastError(self:object) -> str:
		return self.__lastError
	def getTree(self:object, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		if self.isInitialized() and isinstance(indentationSymbol, str) and "\r" not in indentationSymbol and "\n" not in indentationSymbol and isinstance(indentationCount, int) and indentationCount >= 0:
			stack = [(self.__pointerNodeStack[0], 0)]
			res = []
			while stack:
				node, level = stack.pop()
				if node.isInitialized():
					res.append("{0}{1}".format(str(indentationSymbol) * level, os.path.relpath(node.getFilePath(), self.__baseFolderPath)))
					stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			return "\n".join(res)
		else:
			return None

class StructureNode:
	def __init__(self:object, header:str = "", parent:object = None) -> object:
		self.__header = header if isinstance(header, str) else ""
		self.__footer = ""
		self.__type = None # initialization flag
		self.__descriptor = None
		self.__children = None # initialization flag
		self.__parent = parent if isinstance(parent, StructureNode) else None
	def initialize(self:object) -> bool:
		if self.__header:
			if "Root" == self.__header:
				self.__type = "Root"
				self.__descriptor = None
			elif self.__header.startswith("\\begin{") and self.__header.endswith("}"):
				self.__type = "Environment"
				self.__descriptor = self.__header[7:-1] # cannot compile "\\begin{ equation }" in LaTeX
			elif self.__header.startswith("\\documentclass"):
				self.__type = "DocumentClass"
				self.__descriptor = None
			elif (																						\
				(																					\
					self.__header.startswith("\\section{") or self.__header.startswith("\\section*{")					\
					or self.__header.startswith("\\subsection{") or self.__header.startswith("\\subsection*{")			\
					or self.__header.startswith("\\subsubsection{") or self.__header.startswith("\\subsubsection*{")		\
				)																					\
				and self.__header.endswith("}")															\
			):
				self.__type = "S" + self.__header[2:self.__header.index("{")]
				self.__descriptor = self.__header[self.__header.index("{") + 1:-1].strip()
			elif self.__header in ("$", "$$", "\\(", "\\["):
				self.__type = "Equation"
				self.__descriptor = self.__header
			else:
				self.__type = None # avoid re-initialization
				self.__children = None # avoid re-initialization
				return False
			self.__children = []
			return True
		else:
			self.__type = None # avoid re-initialization
			self.__children = None # avoid re-initialization
			return False
	def isInitialized(self:object) -> bool:
		return isinstance(self.__type, str) and isinstance(self.__children, list)
	def addChildStructureNode(self:object, structureNode:object) -> bool:
		if self.isInitialized() and isinstance(structureNode, StructureNode):
			self.__children.append(structureNode)
			return True
		else:
			return None
	def isFooterAccepted(self:object, footer:str) -> bool:
		if self.isInitialized() and isinstance(footer, str):
			if "Root" == footer or footer.startswith("\\documentclass"):
				return self.__type in ("DocumentClass", "Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*")
			elif "\\begin{thebibliography}" == footer:
				return self.__type in ("Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*")
			elif footer.startswith("\\end{") and footer.endswith("}"):
				return (
					"Environment" == self.__type and footer[5:-1] == self.__descriptor
					or "document" == footer[5:-1] and self.__type in ("Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*")
				)
			elif (footer.startswith("\\section{") or footer.startswith("\\section*{") or footer.startswith("\\subsection{") or footer.startswith("\\subsection*{") or footer.startswith("\\subsubsection") or footer.startswith("\\subsubsection*")) and footer.endswith("}"):
				if self.__type in ("Section", "Section*"):
					return footer.startswith("\\section{") or footer.startswith("\\section*{") # only "\\section" and "\\section*" are allowed
				elif self.__type in ("Subsection", "Subsection*"):
					return footer.startswith("\\section{") or footer.startswith("\\section*{") or footer.startswith("\\subsection{") or footer.startswith("\\subsection*{") # >=
				elif self.__type in ("Subsubsection", "Subsubsection*"):
					return True # all the three are accepted
				else:
					return False
			elif footer in ("$", "$$"):
				return "Equation" == self.__type and footer == self.__descriptor
			elif "\\)" == footer:
				return "Equation" == self.__type and "\\(" == self.__descriptor
			elif "\\]" == footer:
				return "Equation" == self.__type and "\\[" == self.__descriptor
			else: # Root etc. 
				return False
		else:
			return None
	def setFooter(self:object, footer:str) -> bool:
		bRet = self.isFooterAccepted(footer)
		if bRet and self.__header not in ("DocumentClass", "Section", "Section*", "Subsection", "Subsubsection"): # the "documentclass" and section-like structures do not require footnotes
			self.__footer = footer
		return bRet
	def addPlainText(self:object, strings:str = "") -> bool:
		if self.isInitialized() and isinstance(strings, str):
			if self.__children and isinstance(self.__children[-1], str): # the last node is a string
				self.__children[-1] += strings
			else: # create a new string
				self.__children.append(strings)
		else:
			return None
	def getType(self:object) -> str:
		return self.__type
	def getChildren(self:object, isReversed:bool = False) -> list:
		return (self.__children[::-1] if isReversed else self.__children[::]) if self.isInitialized() else None
	def getParent(self:object) -> object:
		return self.__parent
	def __str__(self:object) -> str:
		return "{0}".format(self.__type) if self.__descriptor is None else "{0}({1})".format(self.__type, self.__descriptor)

class Structure:
	def __init__(self:object) -> object:
		self.__rootStructureNode = None # initialization flag
		self.__currentStructureNode = None # initialization flag
	def initialize(self:object) -> bool:
		self.__rootStructureNode = StructureNode("Root")
		if self.__rootStructureNode.initialize():
			self.__currentStructureNode = self.__rootStructureNode
			return True
		else:
			self.__rootStructureNode = None # avoid re-initialization
			self.__currentStructureNode = None # avoid re-initialization
			return False
	def isInitialized(self:object) -> bool:
		return isinstance(self.__rootStructureNode, StructureNode) and isinstance(self.__currentStructureNode, StructureNode)
	def addPlainText(self:object, strings:str = "") -> bool:
		return self.__currentStructureNode.addPlainText(strings) if self.isInitialized() else None
	def addStructureNode(self:object, header:str) -> bool:
		if self.isInitialized() and isinstance(header, str):
			while (																									\
				(																									\
					(																								\
						header.startswith("\\documentclass") or header.startswith("\\section{") or header.startswith("\\section*{")			\
						or header.startswith("\\subsection{") or header.startswith("\\subsection*{")									\
						or header.startswith("\\subsubsection{") or header.startswith("\\subsubsection*{")							\
					)																								\
					and header.endswith("}") or "\\begin{thebibliography}" == header											\
				) and self.__currentStructureNode.isFooterAccepted(header)													\
			): # go back to the parent node if the footer is accepted
				self.__currentStructureNode = self.__currentStructureNode.getParent()
			structureNode = StructureNode(header = header, parent = self.__currentStructureNode)
			if structureNode.initialize() and self.__currentStructureNode.addChildStructureNode(structureNode):
				self.__currentStructureNode = structureNode
				return True
			else:
				return False
		else:
			return None
	def canLeaveCurrentStructureNode(self:object, footer:str) -> bool:
		if self.isInitialized() and isinstance(footer, str):
			return self.__currentStructureNode != self.__rootStructureNode and self.__currentStructureNode.isFooterAccepted(footer)
		else:
			return None
	def leaveCurrentStructureNode(self:object, footer:str = "") -> bool:
		bRet = self.canLeaveCurrentStructureNode(footer)
		if bRet:
			self.__currentStructureNode.setFooter(footer)
			self.__currentStructureNode = self.__currentStructureNode.getParent()
		return bRet
	def getCurrentStructureNodeDescription(self:object) -> str:
		return str(self.__currentStructureNode) if self.isInitialized() else None
	def endStructure(self:object) -> bool:
		while self.canLeaveCurrentStructureNode("Root"):
			self.leaveCurrentStructureNode("Root")
		return self.__currentStructureNode == self.__rootStructureNode
	def getTree(self:object, isDetailed:bool = True, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		if self.isInitialized() and isinstance(isDetailed, bool) and isinstance(indentationSymbol, str) and "\r" not in indentationSymbol and "\n" not in indentationSymbol and isinstance(indentationCount, int) and indentationCount >= 0:
			stack = [(self.__rootStructureNode, indentationCount)]
			res = []
			while stack:
				node, level = stack.pop()
				if isinstance(node, str):
					if isDetailed:
						res.append("{0}Text({1})".format(indentationSymbol * level, len(node)))
				elif node.isInitialized() and (isDetailed or node.getType() in ("Root", "DocumentClass", "Environment", "Section", "Section*", "Subsection", "Subsection*", "Subsubsection", "Subsubsection*")):
					res.append("{0}{1}".format(indentationSymbol * level, node))
					stack.extend([(n, level + 1) for n in node.getChildren(isReversed = True)])
			return "\n".join(res)
		else:
			return None

class Checker:
	def __init__(self:object, mainTexPath:str = None, debugLevel:DebugLevel|int = Debug) -> object:
		self.__mainTexPath = os.path.abspath(mainTexPath.replace("\"", "")) if isinstance(mainTexPath, str) else None # transfer to the absolute path
		self.__pointer = None
		self.__structure = None
		self.__definitions = {}
		self.__labels = {}
		self.__citations = {}
		if isinstance(debugLevel, DebugLevel):
			self.__debugLevel = debugLevel
		else:
			try:
				self.__debugLevel = DebugLevel({"value":int(debugLevel)})
			except:
				self.__debugLevel = Debug
				self.__print("The debug level specified is invalid. It is defaulted to {0} ({1}). ".format(self.__debugLevel.name, self.__debugLevel.value), Warning)
		self.__flag = False
	def __print(self:object, strings:str|object, debugLevel:DebugLevel = Info, indentationSymbol:str = "\t", indentationCount:int = 0) -> bool:
		if (isinstance(strings, str) or hasattr(strings, "__str__")) and isinstance(debugLevel, DebugLevel) and isinstance(indentationSymbol, str) and isinstance(indentationCount, int):
			if debugLevel >= self.__debugLevel:
				try:
					print("\n".join(["{0} {1}{2}".format(debugLevel, (indentationSymbol * indentationCount if indentationCount >= 1 else ""), string) for string in str(strings).split("\n")]))
					return True
				except: # avoid exceptions in __str__
					return False
			else:
				return False
		else:
			return None
	def __input(self:object, strings:str, indentationSymbol:str = "\t", indentationCount:int = 0) -> str:
		try:
			return input("\n".join(["{0} {1}{2}".format(Prompt, (indentationSymbol * indentationCount if isinstance(indentationSymbol, str) and isinstance(indentationCount, int) and indentationCount >= 1 else ""), string) for string in str(strings).splitlines()]))
		except KeyboardInterrupt:
			print() # print an empty line
			self.__print("The input process was interrupted by users. None will be returned as the default value. ", Warning)
			return None
		except BaseException as e:
			self.__print("The input process was interrupted by the following exceptions. ", Error)
			self.__print(e, Error, indentationCount = 1)
			return None
	def __skipSpaces(self:object, lineSwitch:bool = True) -> bool:
		if isinstance(lineSwitch, bool):
			while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"): # skip spaces in the current line
				self.__pointer.nextChar(fileSwitch = False)
			if self.__pointer.hasNextChar(fileSwitch = False): # remaining non-space characters exist
				return True
			elif lineSwitch: # allow a line separator
				if self.__pointer.hasNextLine(fileSwitch = False):
					self.__pointer.nextLine(fileSwitch = False)
					while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"): # skip spaces in the following line
						self.__pointer.nextChar(fileSwitch = False)
					if self.__pointer.hasNextChar(fileSwitch = False):
						return True
					else:
						self.__print("There should be only at most a line between the command definition command and the command but there are two more at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
						return False
				else:
					self.__print("While scanning the command, the file reports an EOF signal at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
					return False
			else:
				self.__print("There should be non-space characters at the end of the line at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
		else:
			return None
	def __convertEscaped(self:object, string:str) -> str:
		if isinstance(string, str):
			vec = list(string)
			d = {"\\":"\\\\", "\"":"\\\"", "\'":"\\\'", "\a":"\\a", "\b":"\\b", "\f":"\\f", "\n":"\\n", "\r":"\\r", "\t":"\\t", "\v":"\\v"}
			for i, ch in enumerate(vec):
				if ch in d:
					vec[i] = d[ch]
				elif not ch.isprintable():
					vec[i] = "\\x" + hex(ord(ch))[2:]
			return "".join(vec)
		else:
			return str(string)
	def __handleBibTeX(self:object) -> bool:
		while True:
			if self.__pointer.hasNextChar(fileSwitch = False) and "@" == self.__pointer.getNextChar(fileSwitch = False):
				# Citation #
				line = self.__pointer.getCurrentLine()
				if "{" in line and "," in line:
					citation = line[line.index("{") + 1:line.index(",")]
				else:
					self.__print("A line starting with \"@\" contains unexpected citation information at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Warning)
					if self.__pointer.hasNextLine(fileSwitch = False):
						self.__pointer.nextLine(fileSwitch = False)
						continue # stop reading citation content and operating the dict
					else:
						self.__pointer.nextLine() # will switch to the parent pointer
						return True
				
				# Citation Content #
				citationContent = ""
				while self.__pointer.hasNextLine(fileSwitch = False):
					self.__pointer.nextLine(fileSwitch = False)
					if self.__pointer.hasNextChar(fileSwitch = False) and "}" == self.__pointer.getNextChar(fileSwitch = False):
						citationContent = citationContent[:-1] # remove the last "\n"
						break
					else:
						citationContent += self.__pointer.getCurrentLine().strip() + "\n"
				
				# Handle Dict #
				if citation in self.__citations:
					if self.__citations[citation][0] is None:
						self.__citations[citation][0] = citationContent
					elif isinstance(self.__citations[citation], list):
						self.__citations[citation][0].append(citationContent)
						self.__print(																													\
							"The citation \"{0}\" has already been defined {1} but is defined again at {2}. ".format(													\
								self.__convertEscaped(citation), "twice" if 2 == length else "for {0} times".format(length), self.__pointer.getCurrentLocationDescription()		\
							), Warning																												\
						)
					else:
						self.__citations[citation][0] = [self.__citations[citation][0], citationContent]
						self.__print("The citation \"{0}\" has already existed but is defined again at {1}. ".format(self.__convertEscaped(citation), self.__pointer.getCurrentLocationDescription()), Warning)
				else:
					self.__citations[citation] = [citationContent, 0] # [citationContent, citeCount]
					self.__print("A new citation \"{0}\" is added by BibTeX at {1}. ".format(self.__convertEscaped(citation), self.__pointer.getCurrentLocationDescription()), Debug)
			if self.__pointer.hasNextLine(fileSwitch = False):
				self.__pointer.nextLine(fileSwitch = False)
			else:
				self.__pointer.nextLine() # will switch to the parent pointer
				return True
	def __resolve(self:object) -> bool:
		self.__pointer = Pointer(self.__mainTexPath)
		self.__structure = Structure()
		self.__definitions.clear()
		self.__labels.clear()
		self.__citations.clear()
		self.__flag = False
		if not self.__pointer.initialize():
			self.__print("Failed to initialize the main tex file. Please check if the file can be read. ", Error)
			return False
		if not self.__structure.initialize():
			self.__print("Failed to initialize the root structure node. ", Error)
			return False
		buffer = "" # can also use a flag to control the buffer like {0:"plainTextBuffer", 1:"commandBuffer", 2:"mandatoryArgumentBuffer", 3:"optionalArguementBuffer"}
		stack = [] # indicate the layer of {}
		isLeftPart = True # indicate the "$" or "$$" got is the left part or not
		while True:
			if self.__pointer.hasNextChar(): # if there is a character following the current character in this line
				self.__pointer.nextChar() # move to the next character
				ch = self.__pointer.getCurrentChar() # get the currenct character
				if "\\" == ch: # use the active modes
					if self.__pointer.hasNextChar(fileSwitch = False):
						if self.__pointer.getNextChar(fileSwitch = False) in ("(", "["):
							self.__structure.addStructureNode("\\" + self.__pointer.getNextChar(fileSwitch = False))
							self.__pointer.nextChar(fileSwitch = False)
						elif self.__pointer.getNextChar(fileSwitch = False) in (")", "]"):
							if not (self.__structure.canLeaveCurrentStructureNode("\\" + self.__pointer.getNextChar(fileSwitch = False)) and self.__structure.leaveCurrentStructureNode("\\" + self.__pointer.getNextChar(fileSwitch = False))):
								self.__print("Cannot end the current environment ({0}) with command \"{1}\" at {2}. ".format(self.__structure.getCurrentStructureNodeDescription(), buffer, self.__pointer.getCurrentLocationDescription()), Error)
								return False
						else:
							buffer = "\\" # initial a buffer to obtain the command
							while self.__pointer.hasNextChar(fileSwitch = False): # fetch the whole command
								ch = self.__pointer.getNextChar(fileSwitch = False)
								if "A" <= ch <= "Z" or "a" <= ch <= "z":
									buffer += ch
									self.__pointer.nextChar(fileSwitch = False)
								else:
									break
							if buffer in ("\\section", "\\subsection", "\\subsubsection") and self.__pointer.hasNextChar(fileSwitch = False) and "*" == self.__pointer.getNextChar(fileSwitch = False): # section*-like structures
								buffer += "*"
								self.__pointer.nextChar(fileSwitch = False)
							if "\\" == buffer: # "\\"
								if "0" <= ch <= "9": # e.g. "\\0" (ch must be defined since judging whether there is a following character is done before)
									self.__pointer.nextChar(fileSwitch = False) # for printing purposes
									self.__print("A command should only contain letters but it does not at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
									return False
								else: # e.g. "\\%" (absorb the next character)
									self.__pointer.nextChar(fileSwitch = False)
									self.__structure.addStructureNode("\\" + self.__pointer.getCurrentChar())
							elif "\\documentclass" == buffer:
								if self.__structure.addStructureNode(buffer):
									self.__print("A new structure node [{0}] is added. ".format(self.__structure.getCurrentStructureNodeDescription()), Debug)
								else:
									self.__print("Failed to initialize a new structure node via \"{0}\" at {1}. ".format(buffer, self.__pointer.getCurrentLocationDescription()), Error)
									return False
							elif buffer in ("\\begin", "\\bibliography", "\\end", "\\input", "\\section", "\\section*", "\\subsection", "\\subsection*", "\\subsubsection", "\\subsubsection*"):
								commandName = buffer[1:] # for judging environments
								while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar() in (" ", "\t"): # skip all the spaces and tabs in the current line
									self.__pointer.nextChar(fileSwitch = False)
								if not self.__pointer.hasNextChar(fileSwitch = False): # allow one "\n" in the same file
									if self.__pointer.hasNextLine(fileSwitch = False):
										self.__pointer.nextLine(fileSwitch = False)
									else:
										self.__structure.addPlainText(buffer)
										continue
								while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar() in (" ", "\t"): # skip all the spaces and tabs in the current line
									self.__pointer.nextChar(fileSwitch = False)
								if not self.__pointer.hasNextChar(fileSwitch = False):
									if self.__pointer.hasNextLine(): # "\\input\n\n" (allow line switch here)
										self.__pointer.nextLine()
										self.__structure.addPlainText(buffer + "\n\n")
										continue
									else: # EOF
										self.__pointer.nextChar()
										continue
								if self.__pointer.hasNextChar(fileSwitch = False):
									ch = self.__pointer.getNextChar()
									if "{" == ch:
										while self.__pointer.hasNextChar(fileSwitch = False): # fetch the string within the {} like the file path
											ch = self.__pointer.getNextChar(fileSwitch = False)
											buffer += ch
											if "}" == ch: # finish fetching
												if "begin" == commandName:
													if self.__structure.addStructureNode(buffer):
														self.__print("A new structure node [{0}] is added. ".format(self.__structure.getCurrentStructureNodeDescription()), Debug)
														if buffer == "\\begin{thebibliography}":
															self.__pointer.nextChar()
															if not self.__skipSpaces():
																return False
															self.__pointer.nextChar()
															ch = self.__pointer.getCurrentChar()
															if "{" == ch:
																layerCount = 1
																while layerCount:
																	if self.__pointer.hasNextChar():
																		self.__pointer.nextChar()
																		ch = self.__pointer.getCurrentChar()
																		if "{" == ch:
																			layerCount += 1
																		elif "}" == ch:
																			layerCount -= 1
																		elif "\\" == ch:
																			if self.__pointer.hasNextChar():
																				self.__pointer.nextChar()
																			elif self.__pointer.hasNextLine():
																				self.__pointer.nextLine()
																			else:
																				self.__print(																													\
																					"An EOF signal is reported while scanning the escaped placeholder(s) in the \"{{}}\" for the \"\\begin{thebibliography}\" command at {0}. ".format(	\
																						self.__pointer.getCurrentLocationDescription()																				\
																					), Error																													\
																				)
																				return False
																	elif self.__pointer.hasNextLine():
																		self.__pointer.nextLine()
																	else:
																		self.__print(																														\
																			"An EOF signal is reported while scanning the non-escaped placeholder(s) in the \"{{}}\" for the \"\\begin{thebibliography}\" command at {0}. ".format(	\
																				self.__pointer.getCurrentLocationDescription()																					\
																			), Error																														\
																		)
															else:
																if "\\" == ch: # handle the placeholder in the form of "\\#"
																	if self.__pointer.hasNextChar():
																		self.__pointer.nextChar()
																	elif self.__pointer.hasNextLine():
																		self.__pointer.nextLine()
																	else:
																		self.__print("An EOF signal is reported while scanning the character after \"\\\" at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
																		return False
																while True:
																	if self.__pointer.hasNextChar():
																		ch = self.__pointer.getNextChar()
																		if ch in (" ", "\t"):
																			self.__pointer.nextChar()
																		elif "\\" == ch:
																			remainingLine = self.__pointer.getRemainingCharactersInTheCurrentLineOfTheCurrentFile()
																			if remainingLine.startswith("\\bibitem"):
																				break
																			else:
																				self.__print(																											\
																					"Without a pair of \"{{}}\" surrounded, the \"\\bibitem\" command instead of others should be right after the placeholder at {0}. ".format(	\
																						self.__pointer.getCurrentLocationDescription()																		\
																					), Error																											\
																				)
																		else:
																			self.__print(																								\
																				"Without a pair of \"{{}}\" surrounded, the \"\\bibitem\" command should be right after the placeholder at {0}. ".format(		\
																					self.__pointer.getCurrentLocationDescription()															\
																				), Error																								\
																			)
																			return False
																	elif self.__pointer.hasNextLine():
																		self.__pointer.nextLine()
																	else:
																		self.__print("An EOF signal is reported while scanning the citations at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
																		return False
													else:
														self.__print("Failed to initialize a new structure node via \"{0}\" at {1}. ".format(buffer, self.__pointer.getCurrentLocationDescription()), Error)
														return False
												elif "bibliography" == commandName:
													if self.__pointer.addPointerNode(buffer[buffer.index("{") + 1:-1]) or self.__pointer.addPointerNode(buffer[buffer.index("{") + 1:-1] + ".bib"):
														self.__print("A new Bib pointer node \"{0}\" is added. ".format(self.__pointer.getCurrentLocation()[0]), Debug)
														if self.__handleBibTeX():
															break # break the loop for fetching the string within the {} to avoid moving to the next character repeatedly
														else:
															return False
													else:
														self.__print("Failed to add a Bib pointer node at {0}. Details are as follows. \n{1}".format(self.__pointer.getCurrentLocationDescription(), self.__pointer.getLastError()), Warning)
												elif "end" == commandName:
													if self.__structure.canLeaveCurrentStructureNode(buffer) and self.__structure.leaveCurrentStructureNode(buffer):
														self.__print("Leave current structure node with \"{0}\". ".format(buffer), Debug)
													else:
														self.__print(																							\
															"Cannot end the current environment [{0}] with command \"{1}\" at {2}. ".format(								\
																self.__structure.getCurrentStructureNodeDescription(), buffer, self.__pointer.getCurrentLocationDescription()		\
															), Error																							\
														)
														return False
												elif "input" == commandName:
													if self.__pointer.addPointerNode(buffer[buffer.index("{") + 1:-1]):
														self.__print("A new TeX pointer node \"{0}\" is added. ".format(self.__pointer.getCurrentLocation()[0]), Debug)
													else:
														self.__print("Failed to add a TeX pointer node at {0}. Details are as follows. \n{1}".format(self.__pointer.getCurrentLocationDescription(), self.__pointer.getLastError()), Warning)
												else:
													self.__structure.addStructureNode(buffer)
												self.__pointer.nextChar(fileSwitch = False)
												break # break the loop for fetching the string within the {}
											else:
												self.__pointer.nextChar(fileSwitch = False)
										else:
											self.__print("Pointer ends when waiting for a \"}}\" for \"{{\" at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
									elif "\\" == ch: # "\\input\\"
										self.__structure.addPlainText(buffer)
									else:
										self.__print("An unexpected character \"{0}\" follows the \"\\{1}\" command at {2}. ".format(("\\\"" if "\"" == ch else ch), commandName, self.__pointer.getCurrentLocationDescription()), Error)
										return False
							elif buffer in ("\\bibitem", "\\label", "\\ref", "\\eqref"):
								if not self.__skipSpaces():
									return False
								
								# Fetch #
								self.__pointer.nextChar(fileSwitch = False)
								if "{" == self.__pointer.getCurrentChar():
									label = ""
									while True:
										if self.__pointer.hasNextChar(fileSwitch = False):
											self.__pointer.nextChar(fileSwitch = False)
											ch = self.__pointer.getCurrentChar()
											if ch in ("\\", "{"):
												self.__print(																									\
													"An unexpected character \"{0}\" appears while scanning the {1} at {2}. ".format(										\
														self.__convertEscaped(ch), "citation" if "\\bibitem" == buffer else "label", self.__pointer.getCurrentLocationDescription()	\
													), Error																									\
												)
												return False
											elif "}" == ch:
												break
											else:
												label += ch
										elif self.__pointer.hasNextLine(fileSwitch = False):
											self.__pointer.nextLine(fileSwitch = False)
											label += "\n"
											while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"):
												self.__pointer.nextChar(fileSwitch = False)
												citation += self.__pointer.getCurrentChar()
											if not self.__pointer.hasNextChar(fileSwitch = False):
												self.__print("Two or more consecutive line breaks are not allowed during the label scanning at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
												return False
										else:
											self.__print("An EOF signal is reported while scanning the label at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
								elif "\\label" == buffer and self.__structure.getCurrentStructureNodeDescription() in ("Environment(equation)", "Environment(equation*)"):
									self.__print("Must use a \"{{\" to follow the \"\\label\" command in the equation environment at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
									return False
								else:
									label = self.__pointer.getCurrentChar()
								
								# Handle #
								if "\\bibitem" == buffer:
									# Environment Check #
									if "Environment(thebibliography)" != self.__structure.getCurrentStructureNodeDescription():
										self.__print("The command \"\\bibitem\" should only be used in the \"thebibliography\" environment. ", Warning)
										# return False
									
									# Fetch Citation Content #
									citationContent = ""
									while True:
										if self.__pointer.hasNextChar():
											ch = self.__pointer.getNextChar()
											if "\\" == ch:
												remainingLine = self.__pointer.getRemainingCharactersInTheCurrentLineOfTheCurrentFile()
												if remainingLine.startswith("\\begin") or remainingLine.startswith("\\bibitem") or remainingLine.startswith("\\end"):
	 												break
											elif "&" == ch:
												citationContent += "&"
												self.__print("Please use \"\\&\" in the citation content at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Warning)
											else:
												citationContent += ch
											self.__pointer.nextChar()
										elif self.__pointer.hasNextLine():
											self.__pointer.nextLine()
											citationContent += "\n"
									
									# Handle Dict #
									if label in self.__citations:
										if self.__citations[label][0] is None:
											self.__citations[label][0] = citationContent
										elif isinstance(self.__citations[label][0], list):
											length = len(self.__citations[label][0])
											self.__print(																													\
												"The citation \"{0}\" has already been defined {1} but is defined again at {2}. ".format(													\
													self.__convertEscaped(label), "twice" if 2 == length else "for {0} times".format(length), self.__pointer.getCurrentLocationDescription()		\
												), Warning																												\
											)
										else:
											self.__citations[label][0] = [self.__citations[label][0], False]
											self.__print("The citation \"{0}\" has already existed but is defined again at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Warning)
									else:
										self.__citations[label] = [citationContent, 0] # [citationContent, citeCount]
										self.__print("A new citation \"{0}\" is added via the \"\\bibitem\" command at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Debug)
								elif "\\label" == buffer:
									if label in 	self.__labels:
										if self.__labels[label][0] is None:
											self.__labels[label][0] = self.__structure.getCurrentStructureNodeDescription()
										elif isinistance(self.__labels[label][0], list):
											length = len(self.__labels[label][0])
											self.__print(																													\
												"The label \"{0}\" has already been defined {1} but is defined again at {2}. ".format(														\
													self.__convertEscaped(label), "twice" if 2 == length else "for {0} times".format(length), self.__pointer.getCurrentLocationDescription()		\
												), Warning																												\
											)
											self.__labels[label][0].append(self.__pointer.getCurrentLocationDescription())
										else:
											self.__labels[label][0] = [self.__labels[label][0], self.__pointer.getCurrentLocationDescription()]
											self.__print("The label \"{0}\" has already existed but is defined again at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Warning)
									else:
										self.__labels[label] = [self.__structure.getCurrentStructureNodeDescription(), 0, 0] # [type, refCount, eqrefCount]
										self.__print("A new label \"{0}\" is added at {1}. ".format(self.__convertEscaped(label), self.__pointer.getCurrentLocationDescription()), Debug)
								else:
									if label in self.__labels:
										self.__labels[label][2 if "\\eqref" == buffer else 1] += 1
									elif "\\eqref" == buffer:
										self.__labels[label] = [None, 0, 1] # [undefined, refCount, eqrefCount]
									else:
										self.__labels[label] = [None, 1, 0] # [undefined, refCount, eqrefCount]
							elif "\\cite" == buffer:
								if not self.__skipSpaces():
									return False
								
								# Fetch #
								if "{" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									citation = ""
									while True:
										if self.__pointer.hasNextChar(fileSwitch = False):
											self.__pointer.nextChar(fileSwitch = False)
											ch = self.__pointer.getCurrentChar()
											if ch in ("\\", "{"):
												self.__print("An unexpected character \"{0}\" appears while scanning the citation at {1}. ".format(self.__convertEscaped(ch), self.__pointer.getCurrentLocationDescription()), Error)
												return False
											elif "}" == ch:
												citations = [item.lstrip() for item in citation.split(",")]
												break
											else:
												citation += ch
										elif self.__pointer.hasNextLine(fileSwitch = False):
											self.__pointer.nextLine(fileSwitch = False)
											citation += "\n"
											while self.__pointer.hasNextChar(fileSwitch = False) and self.__pointer.getNextChar(fileSwitch = False) in (" ", "\t"):
												self.__pointer.nextChar(fileSwitch = False)
												citation += self.__pointer.getCurrentChar()
											if not self.__pointer.hasNextChar(fileSwitch = False):
												self.__print("Two or more consecutive line breaks are not allowed during the citation scanning at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
												return False
										else:
											self.__print("An EOF signal is reported while scanning the citation at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
								else:
									self.__pointer.nextChar(fileSwitch = False)
									citations = [self.__pointer.getCurrentChar()]
								
								# Handle #
								for citation in citations:
									if citation in self.__citations:
										self.__citations[citation][1] += 1
									else:
										self.__citations[citation] = [None, 1] # [undefined, citeCount]
							elif buffer in ("\\newcommand", "\\renewcommand"):
								# Command #
								if not self.__skipSpaces(False):
									return False
								if "{" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									if self.__pointer.hasNextChar(fileSwitch = False) and "\\" == self.__pointer.getNextChar(fileSwitch = False):
										self.__pointer.nextChar(fileSwitch = False)
										bucketFlag = True
									else:
										self.__print("The command to be defined should be right after the \"\\newcommand{{\" or the \"\\renewcommand{{\" at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
										return False
								elif "\\" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									bucketFlag= False
								else:
									self.__print("The command to be defined should be right after the \"\\newcommand\" or the \"\\renewcommand\" at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
									return False
								newcommand = "\\"
								while self.__pointer.hasNextChar(fileSwitch = False):
									ch = self.__pointer.getNextChar(fileSwitch = False)
									if "A" <= ch <= "Z" or "a" <= ch <= "z":
										newcommand += ch
										self.__pointer.nextChar(fileSwitch = False)
									else:
										break
								if not self.__skipSpaces(): # check after the command
									return False
								if bucketFlag:
									if "}" == self.__pointer.getNextChar(fileSwitch = False):
										self.__pointer.nextChar(fileSwitch = False)
									else:
										self.__print("A missing \"}\" is detected when scanning the command definition command at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
										return False
								
								# Option count #
								if not self.__skipSpaces():
									return False
								if "[" == self.__pointer.getNextChar(fileSwitch = False):
									self.__pointer.nextChar(fileSwitch = False)
									if not self.__skipSpaces():
										return False
									counter = ""
									while True:
										if self.__pointer.hasNextChar(fileSwitch = False):
											ch = self.__pointer.getNextChar(fileSwitch = False)
											self.__pointer.nextChar(fileSwitch = False)
											if "0" <= ch <= "9":
												counter += ch
											elif "]" == ch:
												break
											else:
												self.__print(																				\
													"Only digits instead of the character \"{0}\" can be used to indicate the option count at {1}. ".format(	\
														"\\" + ch if ch in ("\\", "\"", "\'") else ch, self.__pointer.getCurrentLocationDescription()			\
													), Error																				\
												)
												return False
										elif not self.__skipSpaces():
											return False
									try:
										counter = int(counter)
									except:
										self.__print("Cannot convert the counter \"{0}\" into a positive integer at {1}. ".format(counter, self.__pointer.getCurrentLocationDescription()), Error)
										return False
									if counter < 1 or counter > 9:
										self.__print("The count of options must be a positive integer not greater than 9. ", Error)
										return False
								else:
									counter = None
								
								# Default value for the first option #
								if not self.__skipSpaces():
									return False
								if "[" == self.__pointer.getNextChar(fileSwitch = False): # must be the default value option
									layer, defaultValue = 1, "["
									self.__pointer.nextChar(fileSwitch = False)
									while layer:
										if self.__pointer.hasNextChar(fileSwitch = False):
											self.__pointer.nextChar(fileSwitch = False)
											ch = self.__pointer.getCurrentChar()
											defaultValue += ch
											if "\\" == ch:
												if self.__pointer.hasNextChar(fileSwitch = False):
													self.__pointer.nextChar(fileSwitch = False)
													defaultValue += self.__pointer.getCurrentChar()
												elif self.__pointer.hasNextLine(fileSwitch = False):
													self.__pointer.nextLine(fileSwitch = False)
													defaultValue += "\n"
												else:
													self.__print("A missing \"]\" is detected when scanning the default value option at {0}. ".self.__pointer.getCurrentLocationDescription(), Error)
													return False
											elif "[" == ch:
												layer += 1
											elif "]" == ch:
												layer -= 1
										elif self.__pointer.hasNextLine(fileSwitch = False):
											self.__pointer.nextLine(fileSwitch = False)
											defaultValue += "\n"
										else:
											self.__print("An EOF signal is reported during scanning the default value at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
									defaultValue = defaultValue[1:-1]
								else:
									defaultValue = None
								
								# Main command body #
								if not self.__skipSpaces():
									return False
								if "{" == self.__pointer.getNextChar(fileSwitch = False):
									layer, mainBody = 1, "{"
									self.__pointer.nextChar(fileSwitch = False)
									while layer:
										if self.__pointer.hasNextChar(fileSwitch = False):
											self.__pointer.nextChar(fileSwitch = False)
											ch = self.__pointer.getCurrentChar()
											mainBody += ch
											if "\\" == ch:
												if self.__pointer.hasNextChar(fileSwitch = False):
													self.__pointer.nextChar(fileSwitch = False)
													mainBody += self.__pointer.getCurrentChar()
												elif self.__pointer.hasNextLine(fileSwitch = False):
													self.__pointer.nextLine(fileSwitch = False)
													mainBody += "\n"
												else:
													self.__print("A missing \"}\" is detected when scanning the main body at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
													return False
											elif "{" == ch:
												layer += 1
											elif "}" == ch:
												layer -= 1
										elif self.__pointer.hasNextLine(fileSwitch = False):
											self.__pointer.nextLine(fileSwitch = False)
											mainBody += "\n"
										else:
											self.__print("An EOF signal is reported during scanning the main body at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
											return False
									mainBody = mainBody[1:-1]
								else:
									self.__pointer.nextChar(fileSwitch = False)
									mainBody = self.__pointer.getCurrentChar()
									if self.__pointer.hasNextChar(fileSwitch = False):
										self.__print("Only a character is accepted for the main body when there is not a {} at {0}. ".format(self.__pointer.getCurrentLocationDescription()), Error)
										return False
								self.__definitions[newcommand] = [counter, defaultValue, mainBody]
								self.__print("The value of the command \"{0}\" has been set to {1}. ".format(newcommand, self.__definitions[newcommand]), Debug)
							else: # the command is not special
								self.__structure.addPlainText(buffer)
					else: # "\\\n"
						self.__structure.addPlainText("\\")
				elif "%" == ch: # the '\\' will be absorbed in the codes for avoiding "\\%" above if the previous char is '\\'
					self.__structure.addPlainText("\n")
					self.__pointer.nextLine()
				elif "$" == ch: # the '\\' will be absorbed in the codes for avoiding "\\$" above if the previous char is '\\'
					if self.__pointer.hasNextChar(fileSwitch = False) and "$" == self.__pointer.getNextChar(fileSwitch = False):
						self.__pointer.nextChar(fileSwitch = False)
						ch = "$$" # else: ch = "$"
					if isLeftPart:
						if self.__structure.addStructureNode(ch):
							self.__print("A new structure node [{0}] is added. ".format(self.__structure.getCurrentStructureNodeDescription()), Debug)
						else:
							self.__print("Failed to initialize a new structure node via \"{0}\" at {1}. ".format(ch, self.__pointer.getCurrentLocationDescription()), Error)
							return False
					else:
						if self.__structure.canLeaveCurrentStructureNode(ch) and self.__structure.leaveCurrentStructureNode(ch):
							self.__print("Leave current structure node with \"{0}\". ".format(ch), Debug)
						else:
							self.__print("Cannot end the current environment [{0}] with command \"{1}\" at {2}. ".format(self.__structure.getCurrentStructureNodeDescription(), ch, self.__pointer.getCurrentLocationDescription()), Error)
							return False
					isLeftPart = not isLeftPart # switch to the other part
				else:
					self.__structure.addPlainText(ch)
			elif self.__pointer.hasNextLine(): # there is not a following character but a following line
				self.__structure.addPlainText("\n")
				self.__pointer.nextLine() # switch to the next line
			else: # EOF
				if self.__structure.endStructure():
					break
				else:
					self.__print("An overall EOF signal is reported with unclosed structure [{0}]. ".format(self.__structure.getCurrentStructureNodeDescription()), Error)
					return False
		self.__flag = True
		return True
	def __printPointer(self:object) -> None:
		self.__print("Pointer: ", Info)
		self.__print(self.__pointer.getTree(), Info)
	def __printStructure(self:object, isDetailed:bool = False) -> None:
		self.__print("Structure: ", Info)
		self.__print(self.__structure.getTree(isinstance(isDetailed, bool) and isDetailed), Info)
	def __setup(self:object) -> bool:
		try:
			if not isinstance(self.__mainTexPath, str):
				tmpMainTexPath = self.__input("Please input the main tex path: ", Prompt)
				if tmpMainTexPath is None:
					self.__print("Setup cancelled. ", Error)
					return False
				else:
					self.__mainTexPath = tmpMainTexPath.replace("\"", "")
					self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
					return self.__setup()
			elif os.path.isfile(self.__mainTexPath):
				if os.path.splitext(self.__mainTexPath)[1].lower() != ".tex":
					self.__print("The main tex path is set to a file whose extension is not \".tex\". ", Warning)
				return self.__resolve()
			elif os.path.isdir(self.__mainTexPath):
				self.__print("Since a folder was specified, the program is scanning the folder now. ", Info)
				self.__print("If it takes too long time, please use \"Ctrl+C\" to stop the scanning. ", Info)
				possibleTargets = []
				try:
					for root, dirs, files in os.walk(self.__mainTexPath):
						for fileName in files:
							if os.path.splitext(fileName)[1].lower() in (".tex", ):
								possibleTargets.append(os.path.join(root, fileName))
				except KeyboardInterrupt:
					self.__print("Scanning is interrupted by users. The results may be incomplete. ", Warning)
				if len(possibleTargets) > 1:
					self.__print("Possible targets are listed as follows. ", Prompt)
					try:
						length = len(str(len(possibleTargets)))
						for i, target in enumerate(possibleTargets):
							self.__print("{{0:>{0}}} = \"{{1}}\"".format(length).format(i + 1, target), Prompt, indentationCount = 1)
						self.__print("{{0:>{0}}} = I do not wish to select any of them. ".format(length).format(0), Prompt, indentationCount = 1)
					except KeyboardInterrupt:
						print() # print an empty line
						self.__print("\nPrinting is interrupted by users. The results may be incomplete. ", Warning)
					choice = self.__input("Please select a tex file as the main file to continue: ", Prompt)
					try:
						choice = int(choice)
					except:
						pass
					if 0 == choice:
						self.__print("The main tex selection is cancelled by users. ", Warning)
						return False
					elif isinstance(choice, int) and 1 <= choice <= len(possibleTargets): # ID matches
						self.__mainTexPath = possibleTargets[choice - 1]
						self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
						return self.__resolve()
					elif choice in possibleTargets: # exact matches (robust matches are not designed here since some operating systems are case sensitive)
						self.__mainTexPath = choice
						self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
						return self.__resolve()
					else:
						try:
							self.__mainTexPath = choice[int(choice) - 1]
							self.__print("The main tex path is set to \"{0}\". ".format(self.__mainTexPath), Info)
							return self.__resolve()
						except:
							self.__print("Invalid choice is made. Failed to resolve main tex. ", Error)
							return False
				elif len(possibleTargets) == 1:
					self.__mainTexPath = possibleTargets[0]
					self.__print("The main tex path is set to \"{0}\" automatically since there is only one tex file detected. ".format(self.__mainTexPath), Info)
					return self.__resolve()
				else:
					self.__print("No tex files are detected under the specified folder.. ", Error)
					return False
			else:
				self.__print("Setup failed since the main tex cannot be read. ", Error)
				return False
		except KeyboardInterrupt:
			self.__print("The setup procedure is interrupted by users. ", Error)
			return False
		except BaseException as e:
			self.__print("Exceptions occurred during the setup. Details are as follows. ", Critical)
			self.__print(e, Critical, indentationCount = 1)
			return False
	def __selectAnOption(self:object, flag:bool) -> str:
		self.__print("\n" + "#" * 100, Prompt)
		if isinstance(flag, bool) and flag:
			d = {"C":"Clear", "D":"Debug", "E":"Exit", "N":"New", "R":"Reload", "S":"Statistics", "T":"Tree"}
			self.__print(																												\
				"Obtained {0} pointer node(s), {1} brief structure node(s), and {2} detailed structure node(s). ".format(									\
					self.__pointer.getTree().count("\n") + 1, self.__structure.getTree(False).count("\n") + 1, self.__structure.getTree(True).count("\n") + 1		\
				), Info																												\
			)
		else:
			d = {"C":"Clear", "D":"Debug", "E":"Exit", "N":"New", "R":"Reload"}
		self.__print("Possible choices are listed as follows. ", Prompt)
		for key, value in d.items():
			self.__print("{0} = {1}".format(key, value), Prompt, indentationCount = 1)
		choices = self.__input("Please input your choice(s) to continue: ")
		invalid = True
		while invalid:
			for ch in choices.upper():
				if ch not in d:
					choices = self.__input("At least one invalid choice exists. Please retry: ")
					break
			else: # end naturally
				invalid = False
		self.__print("#" * 100 + "\n", Prompt)
		return choices
	def __doSetDebugLevel(self:object) -> bool:
		self.__print("Current debug level is {0} ({1}). ".format(self.__debugLevel.name, self.__debugLevel.value), Prompt)
		d = {"P":Prompt, "C":Critical, "E":Error, "W":Warning, "I":Info, "D":Debug}
		for key, value in d.items():
			self.__print("{0} = {1} ({2})".format(key, value.name, value.value), Prompt, indentationCount = 1)
		ch = self.__input("Please select a debug level to continue: ")
		while ch is not None and ch not in d:
			ch = self.__input("The debug level is invalid. Please retry: ")
		if ch is None:
			self.__print("The debug level has not been changed due to the cancellation caused by users. ", Warning)
			return False
		elif d[ch] == self.__debugLevel:
			self.__print("No changes are made to the debug level. ", Info)
			return True
		else:
			self.__debugLevel = d[ch]
			self.__print("The debug level has been changed to {0}. ".format(self.__debugLevel), Info)
			return True
	def __printStatistics(self:object) -> bool:
		pointerTree, structureBriefTree, structureDetailedTree = self.__pointer.getTree().split("\n"), self.__structure.getTree(False).split("\n"), self.__structure.getTree(True).split("\n")
		self.__print(																						\
			"Obtained {0} pointer node(s), {1} brief structure node(s), and {2} detailed structure node(s). ".format(			\
				len(pointerTree), len(structureBriefTree), len(structureDetailedTree)									\
			), Info																						\
		)
		
		# Tree #
		d = {}
		for line in structureDetailedTree:
			key = line.strip()
			if not key.startswith("Text(") and key not in ("Root", "Environment(algorithmic)", "Environment(tabular)"):
				if key.startswith("Environment("):
					key = key[12:-1]
					if key not in ("document", "thebibliography"):
						key = key.replace("*", "") + "(*)"
				elif "(" in key:
					key = key[:key.index("(")].replace("*", "")
				d.setdefault(key, 0)
				d[key] += 1
		self.__print(d, Info)
		
		# Commands #
		self.__print("Commands defined: {0}".format(self.__definitions), Info)
		
		# Labels #
		repeatedLabels, undefinedLabels, unreferencedLabels, hybridReferencedLabels = [], [], [], []
		for key, value in self.__labels.items():
			if isinstance(value[0], list):
				repeatedLabels.append(key)
			elif value[0] is None:
				undefinedLabels.append(key)
			elif value[0] in ("Environment(equation)", "Environment(equation*)") and value[1] or value[0] not in ("Environment(equation)", "Environment(equation*)") and value[2]:
				hybridReferencedLabels.append(key)
			if not (value[1] or value[2]): # can be lots of labels without being referenced
				unreferencedLabels.append(key)
		
		# Repeated #
		length = len(repeatedLabels)
		if length >= 2:
			self.__print("There are {0} repeated labels found, which are listed as follows. ".format(length), Warning)
			self.__print(repeatedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a repeated label found: \"{0}\". ".format(self.__convertEscaped(repeatedLabels[0])), Warning)
		
		# Undefined #
		length = len(undefinedLabels)
		if length >= 2:
			self.__print("There are {0} undefined labels found, which are listed as follows. ".format(length), Warning)
			self.__print(undefinedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an undefined label found: \"{0}\". ".format(self.__convertEscaped(undefinedLabels[0])), Warning)
		
		# Unreferenced #
		length = len(unreferencedLabels)
		if length >= 2:
			self.__print("There are {0} unreferenced labels found, which are listed as follows. ".format(length), Warning)
			self.__print(unreferencedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an unreferenced label found: \"{0}\". ".format(self.__convertEscaped(unreferencedLabels[0])), Warning)
		
		# Hybrid #
		length = len(hybridReferencedLabels)
		if length >= 2:
			self.__print("There are {0} hybrid referenced labels found, which are listed as follows. ".format(length), Warning)
			self.__print(hybridReferencedLabels, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a hybrid referenced label found: \"{0}\". ".format(self.__convertEscaped(hybridReferencedLabels[0])), Warning)
		
		self.__print("Labels defined for referencing: {0}".format(self.__labels), Info)
		
		# Citations #
		repeatedCitations, undefinedCitations, uncitedCitations, similarCitations, citationBodies = [], [], [], [], {}
		for key, value in self.__citations.items():
			if isinstance(value[0], list):
				repeatedCitations.append(key)
			elif value[0] is None:
				undefinedCitations.append(key)
			else:
				stripped = value[0].strip()
				citationBodies.setdefault(stripped, [])
				citationBodies[stripped].append(key)
			if not value[1]:
				uncitedCitations.append(key)
		for value in citationBodies.values():
			if len(value) >= 2:
				similarCitations.append(value)
		
		# Repeated #
		length = len(repeatedCitations)
		if length >= 2:
			self.__print("There are {0} repeated citation entries found, which are listed as follows. ".format(length), Warning)
			self.__print(repeatedCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a repeated citation entry found: \"{0}\". ".format(self.__convertEscaped(repeatedCitations[0])), Warning)
		
		# Undefined #
		length = len(undefinedCitations)
		if length >= 2:
			self.__print("There are {0} undefined citations found, which are listed as follows. ".format(length), Warning)
			self.__print(undefinedCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an undefined citation found: \"{0}\". ".format(self.__convertEscaped(undefinedCitations[0])), Warning)
		
		# Uncited #
		length = len(uncitedCitations)
		if length >= 2:
			self.__print("There are {0} uncited citations found, which are listed as follows. ".format(length), Warning)
			self.__print(uncitedCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is an uncited citation found: \"{0}\". ".format(self.__convertEscaped(uncitedCitations[0])), Warning)
		
		# Similar #
		length = len(similarCitations)
		if length >= 2:
			self.__print("There are {0} citations found with similar content, which are listed as follows. ".format(length), Warning)
			self.__print(similarCitations, Warning, indentationCount = 1)
		elif 1 == length:
			self.__print("There is a citation found with similar content: {0}. ".format(self.__convertEscaped(similarCitations[0])), Warning)
		
		self.__print("Citations defined for citing: {0}".format(self.__citations), Info)
		
		self.__input("Please press the enter key to continue. ")
		return True
	def __handleFolder(self:object, fd:str) -> bool:
		folder = str(fd)
		if not folder:
			return True
		elif os.path.exists(folder):
			return os.path.isdir(folder)
		else:
			try:
				os.makedirs(folder)
				return True
			except:
				return False
	def __drawTree(self:object, strings:str, path:str) -> bool:
		if isinstance(strings, str) and isinstance(path, str):
			try:
				Digraph = __import__("graphviz").Digraph
			except:
				self.__print("Cannot import ``Digraph`` from ``graphviz``. Please resolve the environment before drawing. ", Error)
				return False
			g = Digraph("Tree", filename = path, node_attr = {"shape":"plain"})
			style = "<<table border=\"1\" cellspacing=\"0\"><tr><td port=\"f0\">{0}</td></tr><tr><td port=\"f1\">{1}</td></tr><tr><td port=\"f2\">{2}</td></tr></table>>"
			g.node("0", label = style.format("0", "Root", " "))
			nodeCount, stack = 0, [(0, 0)] # (node, tab)
			for string in strings.splitlines()[1:]:
				tabCount = string.count("\t")
				if 1 <= tabCount <= stack[-1][1] + 1:
					while stack and stack[-1][1] >= tabCount: # find the parent node
						stack.pop()
					nodeCount += 1
					g.node(str(nodeCount), label = style.format(str(nodeCount), string.lstrip(), " "))
					g.edge(str(stack[-1][0]), str(nodeCount), headport = "n", tailport = "s")
					stack.append((nodeCount, tabCount))
				else:
					self.__print("Failed to draw the tree since the tree indentation is incorrect. ", Error)
					return False
			try:
				g.view()
				return True
			except BaseException as e:
				self.__print("Cannot save the tree due to the following exception. ", Error)
				self.__print(e, Error, indentationCount = 1)
				return False
		else:
			self.__print("As no trees are passed to the drawer, the drawing has not been done. \nPlease make sure that the checker has already constructed the trees correctly. ", Error)
			return False
	def __doPrintTree(self:object) -> bool:
		if self.__flag:
			self.__print("Possible tree drawing options are as follows. ", Prompt)
			d = {																					\
				"PP":"Print the pointer", "PSB":"Print the structure briefly", "PSD":"Print the structure in detail", 		\
				"DP":"Draw the pointer", "DSB":"Draw the structure briefly", "DSD":"Draw the structure in detail", 	\
			}
			for key, value in d.items():
				self.__print("{0} = {1}".format(key, value), Prompt, indentationCount = 1)
			ch = self.__input("Please select an option to continue: ")
			while ch is not None and ch not in d:
				ch = self.__input("The option is invalid. Please retry: ")
			if ch is None:
				self.__print("Nothing has been proceeded due to the cancellation caused by users. ", Warning)
				return False
			elif "P" == ch[0]:
				if "P" == ch[1]:
					self.__printPointer()
				else:
					self.__printStructure("D" == ch[2])
				return True
			elif "D" == ch[0]:
				path = self.__input("Please input a \".gz\" file path to save the figure (leave it empty for default values): ")
				while not (isinstance(path, str) and (not path or path.endswith(".gz"))):
					path = self.__input("The previous input is invalid. Please input a \".gz\" file path to save the figure (leave it empty for default values): ")
				if path is None:
					self.__print("The operation is cancelled by users. ", Warning)
					return False
				elif self.__handleFolder(os.path.split(path)[0]):
					return self.__drawTree(self.__pointer.getTree() if "P" == ch[1] else self.__structure.getTree("D" == ch[2]), path if path else ("pointer.gz" if "P" == ch[1] else "structure.gz"))
				else:
					self.__print("Failed to save the tree since the parent folder is not created. ", Error)
					return False
			else:
				return False
		else:
			self.__print("No trees were built since the resolving has not been processed yet. ", Error)
			return False
	def mainBoard(self:object) -> bool:
		self.__setup()
		while True:
			choices = self.__selectAnOption(self.__flag)
			for ch in choices:
				if "C" == ch:
					clearScreen()
				elif "D" == ch:
					self.__doSetDebugLevel()
				elif "E" == ch:
					return self.__flag
				elif "N" == ch:
					self.__mainTexPath = None
					self.__pointer = None
					self.__structure = None
					self.__flag = False
					self.__setup()
				elif "R" == ch:
					self.__pointer = None
					self.__structure = None
					self.__flag = False
					self.__setup() # still call ``__setup``
				elif "S" == ch:
					self.__printStatistics()
				elif "T" == ch:
					self.__doPrintTree()


def clearScreen(fakeClear:int = 120) -> bool:
	if CLEAR_SCREEN_COMMAND is not None and not os.system(CLEAR_SCREEN_COMMAND):
		return True
	else:
		try:
			print("\n" * int(fakeClear))
		except:
			print("\n" * 120)
		return False

def preExit(countdownTime:int = 5) -> None:
	try:
		cntTime = int(countdownTime)
		length = len(str(cntTime))
	except:
		return
	print()
	while cntTime > 0:
		print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime), end = "")
		try:
			sleep(1)
		except:
			print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(0))
			return
		cntTime -= 1
	print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime))

def main() -> int:
	clearScreen()
	if len(argv) > 2:
		processPool = [os.system(STARTUP_COMMAND_FORMAT.format(executable, __file__, mainTexPath)) for mainTexPath in argv[1:]]
		print(																									\
			"As multiple options were given, {0} child processes have been launched, where {1} succeeded and {2} failed. ".format(		\
				len(processPool), 																					\
				processPool.count(EXIT_SUCCESS), 																	\
				len(processPool) - processPool.count(EXIT_SUCCESS)													\
			)																									\
		)
		preExit()
		return EXIT_SUCCESS if not any(processPool) else EXIT_FAILURE
	else:
		checker = Checker(argv[1] if 2 == len(argv) else None)
		checker.mainBoard()
		preExit()
		return EXIT_SUCCESS if checker else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())