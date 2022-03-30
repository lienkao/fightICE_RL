from py4j.java_gateway import get_field
import pickle
import os
import numpy as np
from random import choice 

class QTableManager(object):
    def __init__(self, folderPath, pklName, method):
        self.folderPath = folderPath
        self.pklName = pklName
        self.pickleFile = open(os.path.join(self.folderPath, self.pklName), method)
    
    def getTable(self):
        self.QTable = pickle.load(self.pickleFile)
        # print("get QTable: ", self.QTable)
        self.pickleFile.close()
        return self.QTable

    def writeTable(self, QTable):
        self.QTable = QTable
        pickle.dump(self.QTable, self.pickleFile)
        self.pickleFile.close()
        return

class RLAI(object):
    def __init__(self, gateway, QTablesFolder):
        # print("__init__")
        self.gateway = gateway
        o = self.gateway.jvm.enumerate.Action
        # actions:         Kick    Crouch Kick  Crouch Strong Kick    Slide Kick       
        self.actions = [o.STAND_B, o.CROUCH_B,     o.CROUCH_FB,    o.STAND_D_DB_BB,
        #                  Projectile    Strong Projectile   Forward Jump Fist   Jump Kick
                         o.STAND_D_DF_FB, o.STAND_D_DF_FC,    o.STAND_D_DB_BA,    o.AIR_B,
        #              Jump Low Kick  Jump Projectile  Jump High Kick  Jump Strong Kick
                         o.AIR_DB,    o.AIR_D_DF_FB,     o.AIR_UB,    o.AIR_F_D_DFB]
        self.frameskip = True
        self.QTablesFolder = QTablesFolder
        
        # greedy parameter
        self.epsilon = 0.8
        # learning rate
        self.learningRate = 0.2
        # future rate
        self.futureRate = 0.2

    def close(self):
        pass
    
    def initialize(self, gameData, player):
        # print("initialize")
        self.inputKey = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.commandCenter = self.gateway.jvm.aiinterface.CommandCenter()
        self.player = player
        self.gameData = gameData
        self.characterName = str(gameData.getCharacterName(self.player))
        self.motionData = self.gameData.getMotionData(self.player)
        self.myCharacter = self.frameData.getCharacter(self.player)
        self.oppCharacter = self.frameData.getCharacter(not self.player)
        self.simulator = self.gameData.getSimulator()

        # now State's X and Y index in Q table
        self.nowXState = -1
        self.nowYState = -1

        # previous State's X and Y index in Q table
        self.preXState = -1
        self.preYState = -1

        # now and previous action's index in actions[]
        self.nowActionIndex = -1
        self.preActionIndex = -1

        # previous State's myHp and oppHp use to count reward
        self.preMyHp = -1
        self.preOppHp = -1

        self.roundCount = 0
        
        # print("in init")

        # if self.characterName == "ZEN":
        # try:
        self.QTManager = QTableManager(self.QTablesFolder, 'ZEN.pkl', "rb")
        self.QTables = self.QTManager.getTable()
        # except:
        #     n_bucket = (5, 9)
        #     n_actions = len(self.actions)
        #     self.QTables = np.zeros(n_bucket + (n_actions,))
            # print(self.QTablesFolder)
            # print(os.path.join(self.QTablesFolder, 'ZEN.pkl'))
            # self.pickleFile = open(os.path.join(self.QTablesFolder, 'ZEN.pkl'), "wb+")
            # pickle.dump( self.QTables, self.pickleFile)
        # print("finish try")
        
        self.isGameJustStarted = True
        return 0

    # please define this method when you use FightingICE version 3.20 or later
    def roundEnd(self, p1hp, p2hp, frames):

        if p1hp <= p2hp:
            print("Lose")
        elif p1hp > p2hp:
            print("Win!")
        print("p1hp:{}, p2hp:{}, frame used: {}".format(p1hp,  p2hp, frames))
        self.nowXState = -1
        self.nowYState = -1
        self.preXState = -1
        self.preYState = -1
        self.nowActionIndex = -1
        self.preActionIndex = -1
        self.preMyHp = -1
        self.preOppHp = -1
        self.roundCount += 1
        if self.roundCount >= 3:
            print("Game End!")
            self.QTManager = QTableManager(self.QTablesFolder, 'ZEN.pkl', "wb+")
            self.QTManager.writeTable(self.QTables)
        return

    # Please define this method when you use FightingICE version 4.00 or later
    def getScreenData(self, sd):
        self.screenData = sd
    
    # update every frame
    def getInformation(self, frameData, isControl):
        # print("getInformation")
        self.frameData = frameData
        self.commandCenter.setFrameData(self.frameData, self.player)
        self.isControl = isControl
        self.myCharacter = self.frameData.getCharacter(self.player)
        self.oppCharacter = self.frameData.getCharacter(not self.player)
        # print("finish getInformation")
    
    def input(self):
        return self.inputKey
    
    def getActionEnergyCost(self, action):
        # print("get Action energy cost")
        ret = abs(self.motionData.get(self.gateway.jvm.enumerate.Action.valueOf(action.name()).ordinal()).getAttackStartAddEnergy())
        # print("complete get energy cost")
        return ret
    

    # return max Q(S+1, A)
    def maxFutureState(self):
        # print("maxFutureState")
        mAction = self.gateway.jvm.java.util.ArrayDeque()
        mAction.add(self.actions[self.preActionIndex])

        futureFrame = self.simulator.simulate(self.frameData, self.player, mAction, None, 60)

        disX = abs(futureFrame.getDistanceX())
        disY = futureFrame.getDistanceY()
        futureX, futureY = self.getState(disX, disY)
        
        return self.QTables[futureX][futureY].max()
    
    ''' update Q table by last time's state and action
    '''
    def updateQTable(self):
        # print("updateQTable")
        reward = abs(self.oppCharacter.getHp() - self.preOppHp) - abs(self.myCharacter.getHp() - self.preMyHp)
        maxFuture = self.maxFutureState()
        x = self.preXState
        y = self.preYState
        act = self.preActionIndex
        # Q(S, A) += LR * (Reward + FR(max(Q(S+1, A))) - Q(S, A))
        updateValue = self.learningRate * (reward + self.futureRate * maxFuture - self.QTables[x][y][act])

        # print("last action reward: ", reward, " maxFuture: ", maxFuture, " update value: ", updateValue)

        self.QTables[x][y][act] += updateValue
        return

    def getCorrespondingValue(self, rangelist, find):
        # print("getCorrespondingValue")
        if find < rangelist[0]:
            return 0
        if find >= rangelist[-1]:
            return len(rangelist)
        for i in range(1, len(rangelist)):
            if rangelist[i-1] <= find < rangelist[i]:
                return i
    ''' 
    discrete now state by  abs(x): <20 20~50 50~85 85~100 100< ; 
                                y: < -200 -200~-100 -100~-40 -40~0 0 0~40 40~100 100~200 200<
    '''
    def getState(self, disX, disY):
        # print("getState")
        # print("disX, disY in getState()", disX, disY)
        XState = self.getCorrespondingValue([20, 50, 85, 100], disX)
        YState = self.getCorrespondingValue([-200, -100, -40, 0, 1, 40, 100, 200], disY)   
        # print("XState, YState in getState()", XState, YState)     
        return XState, YState
    
    '''return avaliable actions list by player's now energy
    '''
    def getAvaliableActions(self):
        # print("getAvaliableActions")
        avaliableActions = []
        for action in self.actions:
            if self.getActionEnergyCost(action) <= self.energy:
                avaliableActions.append(action)
        return avaliableActions
    
    def getBestActionInQTable(self, avaliableActions):
        # print("getBestActionInQTable")
        # print("avaliable actions: ", avaliableActions)
        maxIndex = 0
        # print("X state: ", self.nowXState, " Y state: ", self.nowYState)
        maxValue = self.QTables[self.nowXState][self.nowYState][0]
        # print("maxvalue: ", maxValue)
        for act in avaliableActions:
            nowIndex = self.actions.index(act)
            if self.QTables[self.nowXState][self.nowYState][nowIndex] > maxValue:
                maxValue = self.QTables[self.nowXState][self.nowYState][nowIndex]
                maxIndex = nowIndex
        
        return self.actions[maxIndex]
    
    ''' get Action 80% by State 20% random
    '''
    def getAction(self):
        # print("getAction")
        self.preMyHp = self.myCharacter.getHp()
        self.preOppHp = self.oppCharacter.getHp()
        
        avaliableActions = self.getAvaliableActions()

        # print("complete getAvaliableActions, avaliableActions: ", avaliableActions)
        action = self.gateway.jvm.enumerate.Action.STAND_B
        # print(action)
        # print("start random")
        # action by state
        if np.random.random_sample() <= self.epsilon:
            # print("not random one")
            self.nowXState, self.nowYState = self.getState(abs(self.frameData.getDistanceX()), self.frameData.getDistanceY())
            self.preXState, self.preYState = self.nowXState, self.nowYState
            action = self.getBestActionInQTable(avaliableActions)
        # action by random
        else:
            # print("random one")
            action = choice(avaliableActions)
            # print("random choice done")
        # print("get action ", action)
        return action
    
    def processing(self):
        # print("processing")
        # First we check whether we are at the end of the round
        if self.frameData.getEmptyFlag() or self.frameData.getRemainingTime() <= 0:
            self.isGameJustStarted = True
            return
        
        if not self.isGameJustStarted:
            # Simulate the delay and look ahead 2 frames. The simulator class exists already in FightingICE
            self.frameData = self.simulator.simulate(self.frameData, self.player, None, None, 17)
        else:
            # If the game just started, no point on simulating
            self.isGameJustStarted = False

        self.commandCenter.setFrameData(self.frameData, self.player)    

        if self.commandCenter.getSkillFlag():
            self.inputKey = self.commandCenter.getSkillKey()
            return

        self.inputKey.empty()
        self.commandCenter.skillCancel()

        self.energy = self.myCharacter.getEnergy()
        # print("my energy: ", self.energy)
        # previous action is done, update Q table
        if self.preActionIndex != -1:
            self.updateQTable()
        
        # get action by now state and record it
        action = self.getAction()
        self.preActionIndex = self.actions.index(action)

        self.commandCenter.commandCall(action.name())


    
    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]
