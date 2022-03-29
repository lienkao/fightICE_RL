from py4j.java_gateway import get_field
import logging
import pickle
import os

class RLAI(object):

    def __init__(self, gateway, qtables_folder):
        self.gateway = gateway
        self.just_inited = True
        o = self.gateway.jvm.enumerate.Action
        # actions:          Kick    Crouch Kick  Crouch Strong Kick    Slide Kick       
        self._actions = [o.STAND_B, o.CROUCH_B,     o.CROUCH_FB,    o.STAND_D_DB_BB,
        #                  Projectile    Strong Projectile   Forward Jump Fist   Jump Kick
                         o.STAND_D_DF_FB, o.STAND_D_DF_FC,    o.STAND_D_DB_BA,    o.AIR_B,
        #              Jump Low Kick  Jump Projectile  Jump High Kick  Jump Strong Kick
                         o.AIR_DB,    o.AIR_D_DF_FB,     o.AIR_UB,    o.AIR_F_D_DFB]
        self.frameskip = True
        self.qtables_folder = qtables_folder
        
        # greedy parameter
        self.epsilon = 0.8
        # learning rate
        self.learning_rate = 0.2
        # future rate
        self.future_rate = 0.2
    
    def close(self):
        pass
    
    def initialize(self, gameData, player):
        self.inputKey = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.cc = self.gateway.jvm.aiinterface.CommandCenter()
        self.player = player
        self.gameData = gameData
        self.charaname = str(gameData.getCharacterName(self.player))

        self.last

        if self.charaname == "ZEN":
            fid = open(os.path.join((self.qtables_folder, 'ZEN.pkl')), "rb")
            self.qtables = pickle.load(fid)
            fid.close()
        self.isGameJustStarted = True
        return 0

    # please define this method when you use FightingICE version 3.20 or later
    def roundEnd(self, p1hp, p2hp, frames):
        self.just_inited = True
        if p1hp <= p2hp:
            print("Lost, p1hp:{}, p2hp:{}, frame used: {}".format(p1hp,  p2hp, frames))
        elif p1hp > p2hp:
            print("Win!, p1hp:{}, p2hp:{}, frame used: {}".format(p1hp,  p2hp, frames))

    # Please define this method when you use FightingICE version 4.00 or later
    def getScreenData(self, sd):
        self.screenData = sd
    
    def getInformation(self, frameData, isControl):
        self.frameData = frameData
        self.isControl = isControl
        self.cc.setFrameData(self.frameData, self.player)
        if frameData.getEmptyFlag():
            return
    
    def input(self):
        return self.inputKey
    
    def gameEnd(self):
        # todo: store Q table back
        pass

    # update Q table by last time's state and action
    def updateQTable(self):

    # discrete now state by  abs(x): <20 20~50 50~85 85~100 100< ; 
    #                             y: <-200 -200~-100 -100~-40 -40~0 0 0~40 40~100 100~200 200<
    def getState(self):
        my = self.frameData.getCharacter(self.player)
        opp = self.frameData.getCharacter(not self.player)
        
    
    # get Action 80% by State 20% random
    def getAction(self):

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
        
        # todo: last action is done, update Q table
        self.updateQTable()
        # todo: get action by now state and record it
        action = self.getAction()

        self.cc.commandCall(action)
        if not self.frameskip:
            self.inputKey = self.cc.getSkillKey()


    
    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]