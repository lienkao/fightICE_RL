from py4j.java_gateway import get_field
from py4j.protocol import BOOLEAN_TYPE, DOUBLE_TYPE, INTEGER_TYPE
import math
from random import randint
import logging
import multiprocessing

class Node(object):

	def __init__(self, gateway, frameData, parent, myActions, oppActions, gameData, playerNumber, commandCenter, UCT_TREE_DEPTH = 3, selectedMyActions = []):
		self.gateway = gateway
		
		# UCT excution time
		self.UCT_TIME = 165 * 1000000
		# value for C in UCB1
		self.UCB_C = 3.0
		# depth of tree search
		self.UCT_TREE_DEPTH = UCT_TREE_DEPTH
		# Threshold for generating a node
		self.UCT_CREATE_NODE_THRESHOLD = 10
		# Time for performing simulation
		self.SIMULATION_TIME = 60
		# Use when in need of random numbers
		self.rnd = self.gateway.jvm.java.util.Random()
		# Child node
		self.children = []
		# Node depth
		self.depth = INTEGER_TYPE
		# Number of node visiting times
		self.games = 0
		# UCB1 Value
		self.ucb = 0.
		# Evaluation value
		self.score = 0.

		
		self.isCreateNode = BOOLEAN_TYPE

		self.frameData = frameData
		self.parent = parent
		self.myActions = myActions
		self.oppActions = oppActions
		self.gameData = gameData
		self.simulator = self.gameData.getSimulator()
		self.playerNumber = playerNumber
		self.commandCenter = commandCenter

		self.mAction = self.gateway.jvm.java.util.ArrayDeque()
		self.oppAction = self.gateway.jvm.java.util.ArrayDeque()

		self.myCharacter = self.frameData.getCharacter(playerNumber)
		self.oppCharacter = self.frameData.getCharacter(not playerNumber)
		
		self.myOriginalHp = self.myCharacter.getHp()
		self.oppOriginalHp = self.oppCharacter.getHp()

		if self.parent != None:
			self.depth = self.parent.depth + 1
		else:
			self.depth = 0
		logging.debug("complete depth: ", self.depth)
		self.selectedMyActions = selectedMyActions
		logging.debug("complete __init__")
	
	# Perform MCTS
	# return action of the most visited node

	def mcts(self): # Repeat UCT as many times as possible
		logging.debug("in mcts()")
		start = self.gateway.jvm.java.lang.System.nanoTime()
		
		while self.gateway.jvm.java.lang.System.nanoTime() - start <= self.UCT_TIME:
			self.uct()
		
		return self.getBestScoreAction()
 
 
	# Perform a playout (simulation)
	# return the evaluation value of the playout
	def playout(self):
		self.mAction.clear()
		self.oppAction.clear()
  
		for act in self.selectedMyActions:
			self.mAction.add(act)

		for i in range(5 - len(self.selectedMyActions)):
			self.mAction.add(self.myActions.get(randint(0, len(self.myActions)-1)))

		for i in range(5):
			self.oppAction.add(self.oppActions.get(randint(0, len(self.oppActions)-1)))
		
		# Perform simulation
		nFrameData = self.simulator.simulate(self.frameData, self.playerNumber, self.mAction, self.oppAction, self.SIMULATION_TIME)

		return self.getScore(nFrameData)

	# Perform UCT
	# return the evaluation value
	def uct(self):
		logging.debug("in uct()")
		selectedNode = None
		bestUcb = -99999.0

		for child in self.children:
			logging.debug("in for 1")
			if child.games == 0 :
				logging.debug("in if 1")
    			# I dont know why is 0-49. 
				child.ucb = 9999 + randint(0, 49)
				logging.debug("get rnd nexInt")
			else:
				logging.debug("in else 1")
				child.ucb = self.getUcb(child.score / child.games, self.games, child.games)
			
			if bestUcb < child.ucb :
				logging.debug("in if 2")
				selectedNode = child
				bestUcb = child.ucb
		logging.debug("out for 1")
 
		score = 0.0
		if not selectedNode.games == 0 :
			logging.debug("in selectedNode if")
			score = selectedNode.playout()
		else:
			logging.debug("in selectedNode else")
			if not selectedNode.children:
				if selectedNode.depth < self.UCT_TREE_DEPTH :
					if self.UCT_CREATE_NODE_THRESHOLD <= selectedNode.games :
						selectedNode.createNode()
						selectedNode.isCreateNode = True
						score = selectedNode.uct()
					else:
						score = selectedNode.playout()
				else:
					score = selectedNode.playout()
			else:
				if selectedNode.depth < self.UCT_TREE_DEPTH:
					score = selectedNode.uct()
				else:
					selectedNode.playout()
		
		selectedNode.games += 1
		selectedNode.score += score

		if self.depth == 0 :
			self.games += 1

		return score

	# Generate a node
	def createNode(self):
		for i in range(len(self.myActions)):
			my = []
			for act in self.selectedMyActions:
				my.append(act)
			my.append(self.myActions[i])
			self.children.append(Node(self.gateway, self.frameData, self, self.myActions, self.oppActions, 
										 self.gameData, self.playerNumber, self.commandCenter, self.UCT_TREE_DEPTH, my))

	# Return the action of the most visited node
	# return Action of the most visited node
	def getBestVisitAction(self):
		selected = -1
		bestGames = -9999.0

		for i in range(len(self.children)):
			if bestGames < self.children[i].games :
				bestGames = self.children[i].games
				selected = i

		return self.myActions.get(selected)
	
	# Return the action of the highest score node
	# return Action of the highest score node
	def getBestScoreAction(self):

		selected = []
		bestScore = -9999.0

		for i in range(len(self.children)):
			if self.children[i].games:
				meanScore = self.children[i].score / self.children[i].games
				if bestScore < meanScore :
					bestScore = meanScore
					selected = [i]
				elif bestScore == meanScore :
					selected.append(i)
		
		return self.myActions.get(selected[randint(0, len(selected)-1)])

	# Return the evaluation value
	# param fd frame data (including information such as hp)
 	# return the evaluation value
	def getScore(self, fd):
		return ((fd.getCharacter(self.playerNumber).getHp() - self.myOriginalHp) -
				(fd.getCharacter(not self.playerNumber).getHp() - self.oppOriginalHp))

	# Return the UCB1 value calculated from the evaluation value, the total number of playouts(trails), and the number of playouts of the corresponding action
	# param score Evaluation value
	# param n Total number of trails
	# param ni The number of playouts of the corresponding action
	# return UCB1 value
	def getUcb(self, score, n, ni):
		return score + self.UCB_C * math.sqrt((2 * math.log(n)) / ni)

	class Java:
		implements = ["aiinterface.AIInterface"]