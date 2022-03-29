from py4j.java_gateway import get_field
import pickle
import os
import numpy as np

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
        
        # greedy parameter
        self.epsilon = 0.8
        # learning rate
        self.learningRate = 0.2
        # future rate
        self.futureRate = 0.2

    def close(self):
        pass
    
    def initialize(self, gameData, player):
        self.inputKey = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.cc = self.gateway.jvm.aiinterface.CommandCenter()
        self.player = player
        self.gameData = gameData
        self.charaname = str(gameData.getCharacterName(self.player))
        self.motionData = self.gameData.getMotionData(self.player)
        self.myCharactor = self.frameData.getCharacter(self.player)
        self.oppCharactor = self.frameData.getCharacter(not self.player)
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

        # previos State's myHp and oppHp use to count reward
        self.preMyHp = -1
        self.preOppHp = -1

        # if self.charaname == "ZEN":
        try:
            fid = open(os.path.join((self.qtables_folder, 'ZEN.pkl')), "rb")
            self.QTables = pickle.load(fid)
            fid.close()
        except:
            n_bucket = (5, 9)
            n_actions = len(self.actions)
            self.QTables = np.zeros(n_bucket + (n_actions,))
        
        self.isGameJustStarted = True
        return 0

    # please define this method when you use FightingICE version 3.20 or later
    def roundEnd(self, p1hp, p2hp, frames):
        if p1hp <= p2hp:
            print("Lost, p1hp:{}, p2hp:{}, frame used: {}".format(p1hp,  p2hp, frames))
        elif p1hp > p2hp:
            print("Win!, p1hp:{}, p2hp:{}, frame used: {}".format(p1hp,  p2hp, frames))

    # Please define this method when you use FightingICE version 4.00 or later
    def getScreenData(self, sd):
        self.screenData = sd
    
    # update every frame
    def getInformation(self, frameData, isControl):
        self.frameData = frameData
        self.isControl = isControl
        self.myCharacter = frameData.getCharacter(self.player)
        self.oppCharacter = frameData.getCharacter(not self.player)
        self.energy = self.myCharacter.getEnergy()
        self.cc.setFrameData(self.frameData, self.player)

        if frameData.getEmptyFlag():
            return
    
    def input(self):
        return self.inputKey
    
    
    
    def getActionEnergyCost(self, action):
        return abs(self.myMotion.get(self.gateway.jvm.enumerate.Action.valueOf(action.name()).ordinal()).getAttackStartAddEnergy())
    
    def gameEnd(self):
        # store Q table back
        fid = open(os.path.join((self.qtables_folder, 'ZEN.pkl')), "wb")
        pickle.dump( self.QTables, fid)
        fid.close()
        return 0

    # return max Q(S+1, A)
    def maxFutureState(self):
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
        reward = (self.oppCharactor.getHP() - self.preOppHp) - (self.myCharactor.getHP() - self.preMyHp)
        maxFuture = self.maxFutureState()
        x = self.preXState
        y = self.preYState
        act = self.preActionIndex
        # Q(S, A) += LR * (Reward + FR(max(Q(S+1, A))) - Q(S, A))
        self.QTables[x][y][act] += self.learningRate * (reward + self.futureRate * maxFuture - self.QTables[x][y][act])
        return

    def getCorrespondingValue(self, rangelist, find):
        if find < rangelist[0]:
            return 0
        if find > rangelist[-1]:
            return len(rangelist)
        for i in range(1, len(rangelist)):
            if rangelist[i-1] <= find < rangelist[i]:
                return i
    ''' 
    discrete now state by  abs(x): <20 20~50 50~85 85~100 100< ; 
                                y: < -200 -200~-100 -100~-40 -40~0 0 0~40 40~100 100~200 200<
    '''
    def getState(self, disX, disY):
        XState = self.getCorrespondingValue([20, 50, 85, 100], disX)
        YState = self.getCorrespondingValue([-200, -100, -40, 0, 1, 40, 100, 200], disY)        
        return XState, YState
    
    '''return avalible actions list by player's now energy
    '''
    def getAvalibleActions(self):
        avalibleActions = []
        for action in self.actions:
            if self.getActionEnergyCost(action) <= self.energy:
                avalibleActions.append(action)
        return avalibleActions
    
    def getBestActionInQTable(self):
        return self.actions[self.QTables[self.nowXState][self.nowYState].argmax()]
    
    ''' get Action 80% by State 20% random
    '''
    def getAction(self):
        avalibleActions = self.getAvalibleActions()
        action = self.gateway.jvm.enumerate.Action.STAND_B
        # action by state
        if np.random.random_sample() <= self.epsilon:
            self.nowXState, self.nowYState = self.getState(abs(self.frameData.getDistanceX()), self.frameData.getDistanceY())
            action = self.getBestActionInQTable()
            self.preXState = self.nowXState
            self.preYState = self.nowYState
        # action by random
        else:
            action = np.random.choice(avalibleActions)
        return action
    
    def processing(self):
        if self.frameData.getEmptyFlag() or self.frameData.getRemainingTime() <= 0:
            self.isGameJustStarted = True
            return
        
        if self.frameskip:
            if self.cc.getSkillFlag():
                self.inputKey = self.cc.getSkillKey()
                return
            if not self.isControl:
                return

            self.inputKey.empty()
            self.cc.skillCancel()
        
        # previous action is done, update Q table
        if self.preActionIndex != -1:
            self.updateQTable()
        
        # get action by now state and record it
        action = self.getAction()
        self.preActionIndex = self.actions.index(action)

        self.cc.commandCall(action.name())
        if not self.frameskip:
            self.inputKey = self.cc.getSkillKey()


    
    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]