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

logger = Logging(1)
class QTableManager(object):
    def __init__(self, folderPath, version, pklName, n_bucket:tuple, n_actions:int):
        self.folderPath = folderPath
        self.pickleFileName = os.path.join(os.path.join(folderPath, version), pklName)
        self.n_bucket = n_bucket
        self.n_actions = n_actions
        self.version = version
    
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
        pickleFile = open(os.path.join(os.path.join(self.folderPath, self.version), 'ZEN_{}_record.pkl'.format(self.version)), 'ab+')
        QTable = self.getTable()
        pickle.dump(QTable, pickleFile)
        pickleFile.close()
        return

        

class RLAI(object):
    def __init__(self, gateway, QTablesFolder, version = 'v0.0', train_mode = True, epsilon = 0.9, learningRate = 0.1, futureRate = 0.1):
        
        
        self.gateway = gateway
        o = self.gateway.jvm.enumerate.Action      
        self.actions = [o.AIR_GUARD, o.AIR_A, o.AIR_B, o.AIR_DA, o.AIR_DB,
                        o.AIR_FA, o.AIR_FB, o.AIR_UA, o.AIR_UB, o.AIR_D_DF_FA, o.AIR_D_DF_FB,
                        o.AIR_F_D_DFA, o.AIR_F_D_DFB, o.AIR_D_DB_BA, o.AIR_D_DB_BB, #15
                        o.STAND_B, o.BACK_STEP, o.FORWARD_WALK, o.DASH, o.JUMP, o.FOR_JUMP,
                        o.BACK_JUMP, o.STAND_GUARD, o.CROUCH_GUARD, o.THROW_A, o.THROW_B,
                        o.STAND_A, o.STAND_D_DB_BA, o.CROUCH_A, o.CROUCH_B, o.STAND_FA,
                        o.STAND_FB, o.CROUCH_FA, o.CROUCH_FB, o.STAND_D_DF_FA, o.STAND_D_DF_FB, 
                        o.STAND_F_D_DFA, o.STAND_F_D_DFB, o.STAND_D_DB_BB, o.STAND_D_DF_FC] #
        self.frameskip = True
        self.QTablesFolder = QTablesFolder
        #NOTE: version file
        self.version = version
        self.pklFile = 'ZEN_{}.pkl'.format(version)
        self.train_mode = train_mode
        # greedy parameter
        self.epsilon = epsilon
        if not self.train_mode:
            self.epsilon = 1.0
        # learning rate
        self.learningRate = learningRate
        # future rate
        self.futureRate = futureRate

        self.XStates = [50, 85, 100, 150, 200, 300]
        self.YStates = [-200, -120, -40, 0, 40, 120, 200]
        self.boundXStates = [50, 150, 475, 800, 900]
        self.myPowerStates = [40, 50, 150, 250]
        self.oppPowerStates = [40, 50, 150, 250]

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
        self.nowMyPowerState = -1
        self.nowOppPowerState = -1

        # previous State's X and Y index in Q table
        self.preXState = -1
        self.preYState = -1
        self.preBoundXState = -1
        self.preMyPowerState = -1
        self.preOppPowerState = -1
        # now and previous action's index in actions[]
        self.nowActionIndex = -1
        self.preActionIndex = -1

        # previous State's myHp and oppHp use to count reward
        self.preMyHp = -1
        self.preOppHp = -1

        self.roundCount = 0
        

        # if self.characterName == "ZEN":
        logger.logging("start init QTManager", 0)
        self.QTManager = QTableManager(self.QTablesFolder, self.version, self.pklFile, (len(self.XStates) + 1, len(self.YStates) + 1, len(self.boundXStates) + 1, len(self.myPowerStates) + 1, len(self.oppoPowerStates) + 1), len(self.actions))
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
        self.nowMyPowerState = -1
        self.nowOppPowerState = -1
        self.preXState = -1
        self.preYState = -1
        self.preBoundXState = -1
        self.preMyPowerState = -1
        self.preOppPowerState = -1
        self.nowActionIndex = -1
        self.preActionIndex = -1
        self.preMyHp = -1
        self.preOppHp = -1
        self.roundCount += 1
        if self.roundCount >= 3:
            if self.train_mode:
                print("Game End! MODE: TRAIN")
            else:
                print("Game End! MODE: TEST")
            if self.train_mode :
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
    
    '''return Available actions list by player's now energy
    '''
    def getAvailableActions(self):
        logger.logging("getAvailableActions", 0)
        AvailableActions = []
        if self.myCharacter.getState() == self.gateway.jvm.enumerate.State.AIR:
            for i in range(0, 15):
                if self.getActionEnergyCost(self.actions[i]) <= self.energy:
                    AvailableActions.append(self.actions[i])
        else:
            for i in range(15, 40):
                if self.getActionEnergyCost(self.actions[i]) <= self.energy:
                    AvailableActions.append(self.actions[i])

        return AvailableActions

    # return max Q(S+1, A)
    def maxFutureState(self):
        # print("maxFutureState")
        mAction = self.gateway.jvm.java.util.ArrayDeque()
        mAction.add(self.actions[self.preActionIndex])

        futureFrame = self.simulator.simulate(self.frameData, self.player, mAction, None, 60)

        disX = abs(futureFrame.getDistanceX())
        disY = futureFrame.getDistanceY()
        futureMyPlayer = futureFrame.getCharacter(self.player)
        futureOppPlayer = futureFrame.getCharacter(not self.player)

        absoluteX = futureMyPlayer.getCenterX()
        isFacingRight = futureMyPlayer.isFront()
        faceBoundX = absoluteX
        if isFacingRight: faceBoundX = 960 - absoluteX

        myPower = futureMyPlayer.getEnergy()
        oppPower = futureOppPlayer.getEnergy()

        futureX, futureY, futureBoundX, futureMyPower, futureOppPower = self.getState(disX, disY, faceBoundX, myPower, oppPower)        
        return self.QTables[futureX][futureY][futureBoundX][futureMyPower][futureOppPower].max()
    
    ''' update Q table by last time's state and action
    '''
    def updateQTable(self):
        logger.logging("updateQTable", 0)
        reward = abs(self.oppCharacter.getHp() - self.preOppHp) - abs(self.myCharacter.getHp() - self.preMyHp)
        maxFuture = self.maxFutureState()
        x = self.preXState
        y = self.preYState
        boundX = self.preBoundXState
        myPower = self.preMyPowerState
        oppPower = self.preOppPowerState
        act = self.preActionIndex
        # Q(S, A) += LR * (Reward + FR(max(Q(S+1, A))) - Q(S, A))
        updateValue = self.learningRate * (reward + self.futureRate * maxFuture - self.QTables[x][y][boundX][myPower][oppPower][act])

        logger.logging("last action reward: " + str(reward) + " maxFuture: " + str(maxFuture) + " update value: " + str(updateValue), 0)

        self.QTables[x][y][boundX][myPower][oppPower][act] += updateValue
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
    def getState(self, disX, disY, playerX, myEnergy, oppoEnergy):
        logger.logging("getState", 0)
        logger.logging("disX, disY, playerX in getState() " + str(disX) + " " + str(disY) + " " + str(playerX), 0)
        XState = self.getCorrespondingValue(self.XStates, disX)
        YState = self.getCorrespondingValue(self.YStates, disY)
        boundXState = self.getCorrespondingValue(self.boundXStates, playerX)
        myPowerState = self.getCorrespondingValue(self.myPowerStates, myEnergy)
        oppoPowerState = self.getCorrespondingValue(self.oppoPowerStates, oppoEnergy)
        logger.logging("XState, YState, boundXState powerState in getState() " + str(XState) + ", " + str(YState) + ", " + str(boundXState) + ", " + str(myPowerState) + ", " + str(oppoPowerState), 0)     
        return XState, YState, boundXState, myPowerState, oppoPowerState
    
    
    def getBestActionInQTable(self, actions):
        logger.logging("getBestActionInQTable", 0)
        # print("actions: ", actions)
        maxIndex = 0
        maxValue = self.QTables[self.nowXState][self.nowYState][self.nowBoundXState][self.nowMyPowerState][self.nowOppPowerState][0]
        logger.logging("maxvalue: " + str(maxValue), 0)
        for act in actions:
            nowIndex = self.actions.index(act)
            if self.QTables[self.nowXState][self.nowYState][self.nowBoundXState][self.nowMyPowerState][self.nowOppPowerState][nowIndex] > maxValue:
                maxValue = self.QTables[self.nowXState][self.nowYState][self.nowBoundXState][self.nowMyPowerState][self.nowOppPowerState][nowIndex]
                maxIndex = nowIndex
        
        return self.actions[maxIndex]
    
    ''' get Action 80% by State 20% random
    '''
    def getAction(self):
        # print("getAction")
        self.preMyHp = self.myCharacter.getHp()
        self.preOppHp = self.oppCharacter.getHp()
        AvailableActions = self.getAvailableActions()
        action = self.gateway.jvm.enumerate.Action.STAND_B
        # print(action)
        logger.logging("start random", 0)
        randomNum = np.random.random_sample()
        logger.logging(str(randomNum), 0)
        # action by state
        if randomNum <= self.epsilon:
            logger.logging("not random one", 0)
            absoluteX = self.myCharacter.getCenterX()
            isFacingRight = self.myCharacter.isFront()
            faceBoundX = absoluteX
            if isFacingRight:
                faceBoundX = 960 - absoluteX
                
            self.nowXState, self.nowYState, self.nowBoundXState, self.nowMyPowerState, self.nowOppPowerState = self.getState(abs(self.frameData.getDistanceX()), self.frameData.getDistanceY(), faceBoundX, self.energy, self.oppCharacter.getEnergy())
            logger.logging("complete getState", 0)
            self.preXState, self.preYState, self.preBoundXState, self.preMyPowerState, self.preOppPowerState = self.nowXState, self.nowYState, self.nowBoundXState, self.nowMyPowerState, self.nowOppPowerState
            action = self.getBestActionInQTable(AvailableActions)
        # action by random
        else:
            logger.logging("random one", 0)
            action = choice(AvailableActions)
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
