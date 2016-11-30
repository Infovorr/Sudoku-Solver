import copy
import sys
import time

class SudokuSolver:
	"""
	This class allows for the solving of sudoku puzzles, using one of three algorithms: brute force, backtracking with constraint satisfaction, and forward checking with the MRV heuristic.
	"""

	def readCommand(self, puzzle, name, algorithm, startTime):
		"""
		Takes in a sudoku puzzle, its name, the time at which the program began running, and the specification for which of the three algorithms to use.
		If an invalid algorithm parameter is passed, returns an error.
		"""
		if algorithm == "BF" or algorithm == "BT" or algorithm == "FC-MRV":
			if algorithm == "BF":
				self.bruteForceSearch(puzzle, name, startTime)
			if algorithm == "BT":
				self.backTrackSearch(puzzle, name, startTime)
			if algorithm == "FC-MRV":
				self.forwardCheckSearch(puzzle, name, startTime)
		else:
			return "Just one of BF, BT, or FC-MRV must be passed as an argument."
			
	def bruteForceSearch(self, puzzle, name, pStartTime):
		"""
		Tests every single possible combination of numbers for all blank cells, ignoring constraints, until a solution is found.
		This algorithm will almost certainly never reach the solution in anything resembling a reasonable amount of time.
		"""
		failure = False
		counter = 0
		workingPuzzle = copy.deepcopy(puzzle)
		validCells = workingPuzzle.getCells()
		sStartTime = time.time()
		#Start by assigning the number 1 to all open cells.
		for i in validCells:
			workingPuzzle.setValue(i, 1)
			counter += 1
		#As long as either the puzzle hasn't been solved or the algorithm hasn't failed, work recursively, starting from the first open cell (assuming one begins at A1 and moves right, then down).
		while not workingPuzzle.isValid() and not failure:
			workingPuzzle, failure = self.bruteForceRecursion(workingPuzzle, 0, validCells, failure)
			counter += 1
		endTime = time.time()
		if failure:
			print "No solution exists."
		else:
			self.printSolution(workingPuzzle, name, counter, (endTime - sStartTime), (endTime - pStartTime))
	
	def bruteForceRecursion(self, puzzle, cell, availableCells, failure):
		"""
		Recursive portion of the brute force algorithm.
		Returns either a solved puzzle or a failure.
		"""
		#If the last cell has been reached without finding a solution, return a failure.
		if cell > len(availableCells): #WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
			failure = True
			return puzzle, failure
		#If the current cell is 9, reset to 1 and increment the next cell over.
		if puzzle.getValue(availableCells[cell]) == 9:
			puzzle.setValue(availableCells[cell], 1)
			return self.bruteForceRecursion(puzzle, cell + 1, availableCells, failure)
		puzzle.setValue(availableCells[cell], puzzle.getValue(availableCells[cell]) + 1)
		return puzzle, failure
	
	def backTrackSearch(self, puzzle, name, pStartTime):
		"""
		Uses backtracking and constraint satisfaction to find a solution to the specified sudoku puzzle, taking in the puzzle, its name, and the program start time.
		Either returns a failure, or prints the solution and performance to both the console and two text files.
		"""
		failure = False
		counter = 0
		workingPuzzle = copy.deepcopy(puzzle)
		validcells = workingPuzzle.getCells()
		sStartTime = time.time()
		while not workingPuzzle.isValid() and not failure:
			workingPuzzle, failure, counter = self.backTrackRecursion(workingPuzzle, failure, counter)
		endTime = time.time()
		if failure:
			print "No solution exists."
		else:
			self.printSolution(workingPuzzle, name, counter, (endTime - sStartTime), (endTime - pStartTime))

	def backTrackRecursion(self, puzzle, failure, counter):
		"""
		The recursive portion of the backtrack algorithm.
		Returns either a solved puzzle or a failure.
		"""
		workingPuzzle = copy.deepcopy(puzzle)
		failure = False
		#If all cells have been filled without finding a solution, the algorithm has failed.
		if puzzle.numOpenCells() == 0:
			return puzzle, failure, counter
		#Select the first available cell that has no value.
		currentCell, failure = self.setValue(workingPuzzle, failure)
		for i in workingPuzzle.getRange(currentCell):
			#Try the first possible value for this cell, and then the next if that doesn't work, etc.
			workingPuzzle.setValue(currentCell, i)
			counter += 1
			#Then move to the next available cell.
			workingPuzzle, failure, fCounter = self.backTrackRecursion(workingPuzzle, failure, counter)
			if not failure:
				#If we've reached this point without a failure, then the puzzle has been solved.
				return workingPuzzle, failure, fCounter
			#Otherwise, we've backtracked here and need to try the next available value.
			workingPuzzle, failure = self.resetValue(puzzle, failure)
		failure = True
		return workingPuzzle, failure, counter
		
	def forwardCheckSearch(self, puzzle, name, pStartTime):
		"""
		Uses forward checking and the minimum remaining values heuristic to find a solution to the specified sudoku puzzle, taking in the puzzle, its name, and the program start time.
		Either returns a failure, or prints the solution and performance to both the console and two text files.
		"""
		failure = False
		counter = 0
		workingPuzzle = copy.deepcopy(puzzle)
		validcells = workingPuzzle.getCells()
		sStartTime = time.time()
		while not workingPuzzle.isValid() and not failure:
			workingPuzzle, failure, counter = self.forwardCheckRecursion(workingPuzzle, failure, counter)
		endTime = time.time()
		if failure:
			print "No solution exists."
		else:
			self.printSolution(workingPuzzle, name, counter, (endTime - sStartTime), (endTime - pStartTime))
	
	def forwardCheckRecursion(self, puzzle, failure, counter):
		"""
		The recursive portion of the forward checking algorithm.
		Returns either a solved puzzle or a failure.
		"""
		workingPuzzle = copy.deepcopy(puzzle)
		failure = False
		#If all cells have been filled without finding a solution, the algorithm has failed.
		if puzzle.numOpenCells() == 0:
			return puzzle, failure, counter
		#Try to get a list of all of the cells sharing the smallest number of possible values.
		cellOptions, failure = self.applyMRV(workingPuzzle, failure)
		if not failure:
			#If successful, try the first of those cells...
			for h in cellOptions:
				for i in workingPuzzle.getRange(h):
					#Try the first possible value for this cell, and then the next if that doesn't work, etc.
					workingPuzzle.setValue(h, i)
					counter += 1
					#Then move to the next available cell.
					workingPuzzle, failure, fCounter = self.forwardCheckRecursion(workingPuzzle, failure, counter)
					if not failure:
						#If we've reached this point without a failure, then the puzzle has been solved.
						return workingPuzzle, failure, fCounter
					#Otherwise, we've backtracked here and need to try the next available value.
					workingPuzzle, failure = self.resetValue(puzzle, failure)
				failure = True
				return workingPuzzle, failure, counter
		return workingPuzzle, failure, counter
		
	def printSolution(self, puzzle, name, counter, searchTime, programTime):
		"""
		Prints the solution and performance to the console.
		"""
		solution = puzzle.printBoard()
		print solution
		self.writeSolution(solution, name)
		self.writePerformance(programTime, searchTime, counter, name)
		print "Total clock time: " + str(programTime * 1000)
		print "Search clock time: " + str(searchTime * 1000)
		print "Number of nodes generated: " + str(counter)

	def writeSolution(self, solution, name):
		"""
		Writes the solution to a text file.
		"""
		fName = name[6:]
		file = open("solution" + fName, "w")
		file.write(solution)
		file.close

	def writePerformance(self, pTime, sTime, counter, name):
		"""
		Writes the performance stats to a text file.
		"""
		fName = name[6:]
		file = open("performance" + fName, "w")
		file.write("Total clock time: " + str(pTime * 1000) + "\n")
		file.write("Search clock time: " + str(sTime * 1000) + "\n")
		file.write("Number of nodes generated: " + str(counter) + "\n")
	
	def setValue(self, puzzle, failure):
		"""
		Sets the value of the first unassigned variable in the puzzle.
		"""
		for i in puzzle.getCells():
			if puzzle.getValue(i) == 0:
				return i, failure
		return 0, True
	
	def resetValue(self, puzzle, failure):
		"""
		Resets the puzzle and its values to the last version.
		"""
		resetPuzzle = copy.deepcopy(puzzle)
		return resetPuzzle, failure
	
	def applyMRV(self, puzzle, failure):
		"""
		Selects the unassigned cells that meet the MRV heuristic.
		"""
		cells = puzzle.getSmallestRange()
		if cells is None:
			failure = True
		return cells, failure



class SudokuPuzzle:
	"""
	This class instantiates an object that represents a particular sudoku puzzle, its configuration, and the inherent constraints of sudoku puzzles.
	"""

	def __init__(self, textFile):
		"""
		Initializes a sudoku puzzle using the specified text file.
		"""
		numbers = "123456789"
		letters = "ABCDEFGHI"
		self.keyList = []
		#Generate every possible combination of letters and numbers to create A1 to I9.
		for i in letters:
			for j in numbers:
				self.keyList.append(i + j)
		puzzleFile = open(textFile)
		initialList = []
		#Convert the contents of the text file into a list of individual cells read from left to right, top to bottom, corresponding with A1 to I9.
		for row in puzzleFile:
			initialList.append(row.split())
		puzzleFile.close()
		initialList = initialList[0] + initialList[1] + initialList[2] + initialList[3] + initialList[4] + initialList[5] + initialList[6] + initialList[7] + initialList[8]
		cellList = []
		for i in initialList:
			cellList.append(int(i))
		self.cellReferents = {}
		self.cellRanges = {}
		self.cellValues = {}
		self.fixedCells = []
		#Generate a list of all cells whose values are constrained by the current cell, storing them in a dictionary keyed to this cell.
		for i in self.keyList:
			referents = []
			for j in self.keyList:
				#This grabs all cells in the same row or column.
				if (i[0] in j or i[1] in j) and (i != j) and (j not in referents):
					referents.append(j)
				#The rest of these grab any cells in the same square.
				if (i[0] in "ABC123" and i[1] in "ABC123") and (j[0] in "ABC123" and j[1] in "ABC123") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "DEF123" and i[1] in "DEF123") and (j[0] in "DEF123" and j[1] in "DEF123") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "GHI123" and i[1] in "GHI123") and (j[0] in "GHI123" and j[1] in "GHI123") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "ABC456" and i[1] in "ABC456") and (j[0] in "ABC456" and j[1] in "ABC456") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "DEF456" and i[1] in "DEF456") and (j[0] in "DEF456" and j[1] in "DEF456") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "GHI456" and i[1] in "GHI456") and (j[0] in "GHI456" and j[1] in "GHI456") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "ABC789" and i[1] in "ABC789") and (j[0] in "ABC789" and j[1] in "ABC789") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "DEF789" and i[1] in "DEF789") and (j[0] in "DEF789" and j[1] in "DEF789") and (i != j) and (j not in referents):
					referents.append(j)
				if (i[0] in "GHI789" and i[1] in "GHI789") and (j[0] in "GHI789" and j[1] in "GHI789") and (i != j) and (j not in referents):
					referents.append(j)
			self.cellReferents[i] = referents
			self.cellRanges[i] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		#Set list of possible values for every empty cell, starting with 1-9...
		for i in range(0, 81):
			self.cellValues[self.keyList[i]] = cellList[i]
			if cellList[i] != 0:
				self.fixedCells.append(self.keyList[i])
		#...and then pruning possible values based on the values of any connected cells.
		for i in self.keyList:
			value = self.cellValues[i]
			if value != 0:
				for j in self.cellReferents[i]:
					if value in self.cellRanges[j]:
						tempRange = self.cellRanges[j]
						tempRange.remove(value)
						self.cellRanges[j] = tempRange
		for i in self.fixedCells:
			self.cellRanges[i] = []
	
	def isValid(self):
		"""
		Checks whether the current puzzle configuration meets the constraints.
		"""
		for i in self.keyList:
			value = self.cellValues[i]
			for j in self.cellReferents[i]:
				if value == self.cellValues[j]:
					return False
		return True
		
	def getRange(self, cell):
		"""
		Returns a list of allowed values for the specified cell, according to constraints.
		"""
		return self.cellRanges[cell]
		
	def getCells(self):
		"""
		Returns a list of cells that haven't yet been assigned values.
		"""
		availableCells = copy.deepcopy(self.keyList)
		for i in self.fixedCells:
			availableCells.remove(i)
		return availableCells
		
	def numOpenCells(self):
		"""
		Returns the number of unassigned cells.
		"""
		openCells = 0
		for i in self.keyList:
			if self.cellValues[i] == 0:
				openCells += 1
		return openCells
	
	def setValue(self, cell, value):
		"""
		Sets the value of the specified cell, and prunes the ranges of possible values for all connected cells, according to constraints.
		"""
		self.cellValues[cell] = value
		self.cellRanges[cell] = []
		for i in self.cellReferents[cell]:
			if value in self.cellRanges[i]:
				tempRange = self.cellRanges[i]
				tempRange.remove(value)
				self.cellRanges[i] = tempRange

	def getValue(self, cell):
		"""
		Returns the value of the specified cell.
		"""
		return self.cellValues[cell]
	
	def getSmallestRange(self):
		"""
		Returns a list of the unassigned cells with the fewest possible values, according to MRV.
		"""
		rangeSizes = []
		cellList = self.getCells()
		locations = []
		for i in cellList:
			if len(self.cellRanges[i]) > 0:
				locations.append(i)
				rangeSizes.append(len(self.cellRanges[i]))
		if rangeSizes == []:
			return None
		output = []
		smallest = min(rangeSizes)
		if rangeSizes.count(smallest) > 1:
			for i in range(rangeSizes.count(smallest)):
				output.append(locations[rangeSizes.index(smallest)])
				locations = locations[rangeSizes.index(smallest)+1:]
				rangeSizes = rangeSizes[rangeSizes.index(smallest)+1:]
		else:
			output.append(locations[rangeSizes.index(smallest)])
		return output
			
	def printBoard(self):
		"""
		Returns a 2D string representation of the puzzle.
		"""
		rows = ""
		for h in "ABCDEFGHI":
			for i in self.keyList:
				if i[0] == h:
					rows += str(self.cellValues[i]) + " "
			rows += "\n"
		return rows



if __name__ == "__main__":
	programStart = time.time()
	if len(sys.argv) != 3:
		print "Wrong number of arguments!"
	else:
		puzzle = SudokuPuzzle(sys.argv[1])
		solver = SudokuSolver()
		solver.readCommand(puzzle, sys.argv[1], sys.argv[2], programStart)