from asyncio.log import logger
from py4j.java_gateway import get_field
import pickle
import os
import numpy as np
from random import choice 
 
class Logging(object):
    def __init__(self, mode):
        self.mode = mode
    '''0: debug, 1:info, 2: error
    '''
    def logging(self, msg, level):
        if level >= self.mode:
            print(msg)

logger = Logging(0)
version = 'v4.1'
TRAIN_MODE = True
class QTableManager(object):
    def __init__(self, folderPath, pklName, n_bucket:tuple, n_actions:int):
        self.folderPath = folderPath
        self.pickleFileName = os.path.join(os.path.join(folderPath, version), pklName)
        self.n_bucket = n_bucket
        self.n_actions = n_actions
    
    def createTable(self):
        logger.logging("createTable()", 0)
        QTable = np.zeros(self.n_bucket + (self.n_actions,))
        self.writeTable(QTable)
        logger.logging("created QTable", 0)
        return QTable

    def getTable(self):
        try:
            pickleFile = open(self.pickleFileName, 'rb')
            QTable = pickle.load(pickleFile)
            pickleFile.close()
        except:
            QTable = self.createTable()

        logger.logging("get QTable: ", 0)
        
        return QTable

    def writeTable(self, QTable, file = None):
        logger.logging("in write table", 0)
        if file == None:
            pickleFile = open(self.pickleFileName, 'wb+')
        else:
            pickleFile = open(file, 'wb+')
        pickle.dump(QTable, pickleFile)
        pickleFile.close()
        return
   
    def recordQTableEachGame(self):
        #NOTE: version file
        pickleFile = open(os.path.join(os.path.join(self.folderPath, version), 'ZEN_{}_record.pkl'.format(version)), 'ab+')
        QTable = self.getTable()
        pickle.dump(QTable, pickleFile)
        pickleFile.close()
        return

        

class RLAI(object):
    def __init__(self, gateway, QTablesFolder):
        
        
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
        #NOTE: version file
        self.pklFile = 'ZEN_{}.pkl'.format(version)
        # greedy parameter
        self.epsilon = 0.9
        if not TRAIN_MODE:
            self.epsilon = 1.0
        # learning rate
        self.learningRate = 0.1
        # future rate
        self.futureRate = 0.9

        self.XStates = [50, 85, 100, 150, 200, 300]
        self.YStates = [0, 40, 120, 200]
        self.boundXStates = [50, 150, 475, 800, 900]
        self.powerStates = [20, 40, 50, 150]

    def close(self):
        pass
    
    def initialize(self, gameData, player):
        logger.logging("initialize", 0)
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
        self.nowBoundXState = -1
        self.nowPowerState = -1

        # previous State's X and Y index in Q table
        self.preXState = -1
        self.preYState = -1
        self.preBoundXState = -1
        self.prePowerState = -1
        # now and previous action's index in actions[]
        self.nowActionIndex = -1
        self.preActionIndex = -1

        # previous State's myHp and oppHp use to count reward
        self.preMyHp = -1
        self.preOppHp = -1

        self.roundCount = 0
        

        # if self.characterName == "ZEN":
        logger.logging("start init QTManager", 0)
        self.QTManager = QTableManager(self.QTablesFolder, self.pklFile, (len(self.XStates) + 1, len(self.YStates) + 1, len(self.boundXStates) + 1, len(self.powerStates) + 1), len(self.actions))
        logger.logging("created QTManager", 0)
        self.QTables = self.QTManager.getTable()
        logger.logging("get QTables", 0)    

        logger.logging("finish try", 0)
        
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
        self.nowBoundXState = -1
        self.nowPowerState = -1
        self.preXState = -1
        self.preYState = -1
        self.preBoundXState = -1
        self.prePowerState = -1
        self.nowActionIndex = -1
        self.preActionIndex = -1
        self.preMyHp = -1
        self.preOppHp = -1
        self.roundCount += 1
        if self.roundCount >= 3:
            print("Game End!")
            if TRAIN_MODE :
                self.QTManager.writeTable(self.QTables)
                self.QTManager.recordQTableEachGame()
                logger.logging("Finish store QTable~", 1)
        return

    # Please define this method when you use FightingICE version 4.00 or later
    def getScreenData(self, sd):
        self.screenData = sd
    
    # update every frame
    def getInformation(self, frameData, isControl):
        logger.logging("getInformation", 0)
        self.frameData = frameData
        self.commandCenter.setFrameData(self.frameData, self.player)
        self.isControl = isControl
        self.myCharacter = self.frameData.getCharacter(self.player)
        self.oppCharacter = self.frameData.getCharacter(not self.player)
        logger.logging("finish getInformation", 0)
    
    def input(self):
        return self.inputKey
    
    def getActionEnergyCost(self, action):
        logger.logging("get Action energy cost", 0)
        ret = abs(self.motionData.get(self.gateway.jvm.enumerate.Action.valueOf(action.name()).ordinal()).getAttackStartAddEnergy())
        logger.logging("complete get energy cost", 0)
        return ret
    
    '''return avaliable actions list by player's now energy
    '''
    def getAvaliableActions(self):
        logger.logging("getAvaliableActions", 0)
        avaliableActions = []
        for action in self.actions:
            if self.getActionEnergyCost(action) <= self.energy:
                avaliableActions.append(action)
        return avaliableActions

    # return max Q(S+1, A)
    def maxFutureState(self):
        # print("maxFutureState")
        mAction = self.gateway.jvm.java.util.ArrayDeque()
        mAction.add(self.actions[self.preActionIndex])

        futureFrame = self.simulator.simulate(self.frameData, self.player, mAction, None, 60)

        disX = abs(futureFrame.getDistanceX())
        disY = futureFrame.getDistanceY()
        futurePlayer = futureFrame.getCharacter(self.player)

        absoluteX = futurePlayer.getCenterX()
        isFacingRight = futurePlayer.isFront()
        faceBoundX = absoluteX
        if isFacingRight: faceBoundX = 960 - absoluteX

        power = futurePlayer.getEnergy()

        futureX, futureY, futureBoundX, power = self.getState(disX, disY, faceBoundX, power)
        
        return self.QTables[futureX][futureY][futureBoundX][power].max()
    
    ''' update Q table by last time's state and action
    '''
    def updateQTable(self):
        logger.logging("updateQTable", 0)
        reward = abs(self.oppCharacter.getHp() - self.preOppHp) - abs(self.myCharacter.getHp() - self.preMyHp)
        maxFuture = self.maxFutureState()
        x = self.preXState
        y = self.preYState
        boundX = self.preBoundXState
        power = self.prePowerState
        act = self.preActionIndex
        # Q(S, A) += LR * (Reward + FR(max(Q(S+1, A))) - Q(S, A))
        updateValue = self.learningRate * (reward + self.futureRate * maxFuture - self.QTables[x][y][boundX][power][act])

        logger.logging("last action reward: " + str(reward) + " maxFuture: " + str(maxFuture) + " update value: " + str(updateValue), 0)

        self.QTables[x][y][boundX][power][act] += updateValue
        return

    def getCorrespondingValue(self, rangelist, find):
        logger.logging("getCorrespondingValue", 0)
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
    def getState(self, disX, disY, playerX, energy):
        logger.logging("getState", 0)
        logger.logging("disX, disY, playerX in getState() " + str(disX) + " " + str(disY) + " " + str(playerX), 0)
        XState = self.getCorrespondingValue(self.XStates, disX)
        YState = self.getCorrespondingValue(self.YStates, disY)
        boundXState = self.getCorrespondingValue(self.boundXStates, playerX)
        powerState = self.getCorrespondingValue(self.powerStates, energy)
        logger.logging("XState, YState, boundXState powerState in getState() " + str(XState) + ", " + str(YState) + ", " + str(boundXState) + ", " + str(powerState), 0)     
        return XState, YState, boundXState, powerState
    
    
    def getBestActionInQTable(self, actions):
        logger.logging("getBestActionInQTable", 0)
        # print("actions: ", actions)
        maxIndex = 0
        maxValue = self.QTables[self.nowXState][self.nowYState][self.nowBoundXState][self.nowPowerState][0]
        logger.logging("maxvalue: " + str(maxValue), 0)
        for act in actions:
            nowIndex = self.actions.index(act)
            if self.QTables[self.nowXState][self.nowYState][self.nowBoundXState][self.nowPowerState][nowIndex] > maxValue:
                maxValue = self.QTables[self.nowXState][self.nowYState][self.nowBoundXState][self.nowPowerState][nowIndex]
                maxIndex = nowIndex
        
        return self.actions[maxIndex]
    
    ''' get Action 80% by State 20% random
    '''
    def getAction(self):
        # print("getAction")
        self.preMyHp = self.myCharacter.getHp()
        self.preOppHp = self.oppCharacter.getHp()
        avaliableActions = self.getAvaliableActions()
        action = self.gateway.jvm.enumerate.Action.STAND_B
        # print(action)
        # print("start random")
        # action by state
        if np.random.random_sample() <= self.epsilon:
            # print("not random one")
            absoluteX = self.myCharacter.getCenterX()
            isFacingRight = self.myCharacter.isFront()
            faceBoundX = absoluteX
            if isFacingRight:
                faceBoundX = 960 - absoluteX
                
            self.nowXState, self.nowYState, self.nowBoundXState, self.nowPowerState= self.getState(abs(self.frameData.getDistanceX()), self.frameData.getDistanceY(), faceBoundX, self.energy)
            logger.logging("complete getState", 0)
            self.preXState, self.preYState, self.preBoundXState, self.prePowerState= self.nowXState, self.nowYState, self.nowBoundXState, self.prePowerState
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
        #TODO: when game play update or not
        if self.preActionIndex != -1:
            self.updateQTable()
        
        # get action by now state and record it
        action = self.getAction()
        self.preActionIndex = self.actions.index(action)

        self.commandCenter.commandCall(action.name())


    
    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]
