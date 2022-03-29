from py4j.java_gateway import get_field
from Node import Node
import logging
class MctsAi(object):

    def __init__(self, gateway, UCT_TREE_DEPTH = 3, OppoActionMode = 'self.setOppAction()'):
        self.gateway = gateway
        self.UCT_TREE_DEPTH = UCT_TREE_DEPTH
        self.OppoActionMode = OppoActionMode
        print("UCT_TREE_DEPTH:", self.UCT_TREE_DEPTH)
        print("OppoActionMode:", self.OppoActionMode)

    def close(self):
        pass

    # Load the frame data every time getInformation gets called
    def getInformation(self, frameData, isControl): 
        self.frameData = frameData
        self.commandCenter.setFrameData(self.frameData, self.playerNumber)

        self.myCharacter = frameData.getCharacter(self.playerNumber) # True for player is P1
        self.oppCharacter = frameData.getCharacter(not self.playerNumber)

    def roundEnd(self, x, y, z):
        print(x)
        print(y)
        print(z)
        
    def getScreenData(self, sd):
        pass
        
    def initialize(self, gameData, playerNumber):
        self.playerNumber = playerNumber
        self.gameData = gameData

        self.key = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.commandCenter = self.gateway.jvm.aiinterface.CommandCenter()

        self.myActions = self.gateway.jvm.java.util.LinkedList()
        self.oppActions = self.gateway.jvm.java.util.LinkedList()

        self.simulator = self.gameData.getSimulator()

        self.simulatorAheadFrameData = self.gateway.jvm.struct.FrameData()
        self.myCharacter = self.frameData.getCharacter(playerNumber)
        self.oppCharacter = self.frameData.getCharacter(not playerNumber)

        self.myMotion = self.gateway.jvm.java.util.ArrayList()
        self.oppMotion = self.gateway.jvm.java.util.ArrayList()
        # number of frame to simulate in MCTS
        self.FRAME_AHEAD = 14
        #get actions
        o = self.gateway.jvm.enumerate.Action
        self.actionAir = [o.AIR_GUARD, o.AIR_A, o.AIR_B, o.AIR_DA, o.AIR_DB,
            o.AIR_FA, o.AIR_FB, o.AIR_UA, o.AIR_UB, o.AIR_D_DF_FA, o.AIR_D_DF_FB,
             o.AIR_F_D_DFA, o.AIR_F_D_DFB, o.AIR_D_DB_BA, o.AIR_D_DB_BB]
        self.actionGround = [o.STAND_D_DB_BA, o.BACK_STEP, o.FORWARD_WALK, o.DASH,
             o.JUMP, o.FOR_JUMP, o.BACK_JUMP, o.STAND_GUARD, o.CROUCH_GUARD, o.THROW_A,
             o.THROW_B, o.STAND_A, o.STAND_B, o.CROUCH_A, o.CROUCH_B, o.STAND_FA,
             o.STAND_FB, o.CROUCH_FA, o.CROUCH_FB, o.STAND_D_DF_FA, o.STAND_D_DF_FB, 
             o.STAND_F_D_DFA, o.STAND_F_D_DFB, o.STAND_D_DB_BB]
        self.spSkill = o.STAND_D_DF_FC
        self.rootNode = Node

        self.myMotion = self.gameData.getMotionData(playerNumber)
        self.oppMotion = self.gameData.getMotionData(not playerNumber)

        return 0

    def input(self):
        # The input is set up to the global variable inputKey
        # which is modified in the processing part
        return self.key
    
    # return whether or not the AI can perform an action
    def canProcessing(self):
        return ((not self.frameData.getEmptyFlag()) and (self.frameData.getRemainingTime() > 0))

    def processing(self):
        if self.canProcessing():
            if self.commandCenter.getSkillFlag():
                self.key = self.commandCenter.getSkillKey()
            else:
                self.key.empty()
                self.commandCenter.skillCancel()
                self.mctsPrepare() # Some preparation for MCTS
                logging.debug("complete prepare")
                self.rootNode =	Node(self.gateway, self.simulatorAheadFrameData, None, self.myActions, self.oppActions,
                                          self.gameData, self.playerNumber, self.commandCenter, self.UCT_TREE_DEPTH)
                logging.debug("get rootNode")
                self.rootNode.createNode()
                logging.debug("complete createNode")
                bestAction = self.rootNode.mcts() # Perform MCTS
                logging.debug("get bestAction")
                self.commandCenter.commandCall(bestAction.name()); # Perform an action selected by MCTS
                logging.debug("complete call")

    # Some preparation for MCTS
    # Perform the process for obtaining FrameData with 14 frames ahead
    def mctsPrepare(self):
        self.simulatorAheadFrameData = self.simulator.simulate(self.frameData, self.playerNumber, None, None, self.FRAME_AHEAD)
        logging.debug("complete simulate")
        self.myCharacter = self.simulatorAheadFrameData.getCharacter(self.playerNumber)
        logging.debug("complete my char")
        self.oppCharacter = self.simulatorAheadFrameData.getCharacter(not self.playerNumber)
        logging.debug("complete opp char")
        self.setMyAction()
        logging.debug("complete set myAction")
        logging.debug("myAction: ", self.myActions)
        # for act in self.myActions:
        #     print(act.name())
        eval(self.OppoActionMode)
        logging.debug("complete set oppaction")
        logging.debug("oppAction: ", self.oppActions)
    
    def setMyAction(self):
        self.myActions = self.gateway.jvm.java.util.LinkedList()
        energy = self.myCharacter.getEnergy()

        if self.myCharacter.getState() == self.gateway.jvm.enumerate.State.AIR:
            for act in self.actionAir:
                if abs(self.myMotion.get(self.gateway.jvm.enumerate.Action.valueOf(act.name()).ordinal())
                    .getAttackStartAddEnergy()) <= energy:
                    self.myActions.append(act)
        else:
            if abs(self.myMotion.get(self.gateway.jvm.enumerate.Action.valueOf(self.spSkill.name()).ordinal())
                .getAttackStartAddEnergy()) <= energy:
                self.myActions.append(self.spSkill)
            for act in self.actionGround:
                if abs(self.myMotion.get(self.gateway.jvm.enumerate.Action.valueOf(act.name()).ordinal())
                    .getAttackStartAddEnergy()) <= energy:
                    self.myActions.append(act)
    def setOppAction(self):
        self.oppActions = self.gateway.jvm.java.util.LinkedList()
        energy = self.oppCharacter.getEnergy()

        if self.oppCharacter.getState() == self.gateway.jvm.enumerate.State.AIR:
            for act in self.actionAir:
                if abs(self.oppMotion.get(self.gateway.jvm.enumerate.Action.valueOf(act.name()).ordinal())
                    .getAttackStartAddEnergy()) <= energy:
                    self.oppActions.append(act)
        else:
            if abs(self.oppMotion.get(self.gateway.jvm.enumerate.Action.valueOf(self.spSkill.name()).ordinal())
                .getAttackStartAddEnergy()) <= energy:
                self.oppActions.append(self.spSkill)
            for act in self.actionGround:
                if abs(self.oppMotion.get(self.gateway.jvm.enumerate.Action.valueOf(act.name()).ordinal())
                    .getAttackStartAddEnergy()) <= energy:
                    self.oppActions.append(act)

    def setOppAction_KickAI(self):
        self.oppActions = self.gateway.jvm.java.util.LinkedList()
        self.oppActions.append(self.gateway.jvm.enumerate.Action.STAND_B)

    def setOppAction_ForwardAI(self):
        self.oppActions = self.gateway.jvm.java.util.LinkedList()
        self.oppActions.append(self.gateway.jvm.enumerate.Action.FORWARD_WALK)

    def setOppAction_SkillAI(self):
        self.oppActions = self.gateway.jvm.java.util.LinkedList()
        energy = self.oppCharacter.getEnergy()
        if abs(self.oppMotion.get(self.gateway.jvm.enumerate.Action.valueOf(self.spSkill.name()).ordinal())
            .getAttackStartAddEnergy()) <= energy:
            self.oppActions.append(self.spSkill)
        else:
            self.oppActions.append(self.gateway.jvm.enumerate.Action.BACK_STEP)

    def setOppAction_MacheteAI(self):
        self.oppActions = self.gateway.jvm.java.util.LinkedList()
        # belowing "my" equal to macheteAI, "opp" equal to MctsAI
        
        # init some variable
        distance = self.frameData.getDistanceX()
        my = self.frameData.getCharacter(not self.playerNumber)
        energy = my.getEnergy()
        my_x = my.getLeft()
        my_state = my.getState()
        opp = self.frameData.getCharacter(self.playerNumber)
        opp_x = opp.getLeft()
        opp_state = opp.getState()
        xDifference = my_x - opp_x

        # start rule-base
        if (opp.getEnergy() >= 300) and (my.getHp()- opp.getHp() <= 300):
            self.oppActions.append(self.gateway.jvm.enumerate.Action.FOR_JUMP)
        elif not my_state.equals(self.gateway.jvm.enumerate.State.AIR) and not my_state.equals(self.gateway.jvm.enumerate.State.DOWN):
            if distance > 150:
                self.oppActions.append(self.gateway.jvm.enumerate.Action.FOR_JUMP)
            elif energy >= 300:
                self.oppActions.append(self.gateway.jvm.enumerate.Action.STAND_D_DF_FC)
            elif (distance > 100) and (energy >= 50):
                self.oppActions.append(self.gateway.jvm.enumerate.Action.STAND_D_DB_BB)
            elif opp_state.equals(self.gateway.jvm.enumerate.State.AIR):
                self.oppActions.append(self.gateway.jvm.enumerate.Action.STAND_F_D_DFA)
            elif distance > 100:
                self.oppActions.append(self.gateway.jvm.enumerate.Action.DASH)
            else:
                self.oppActions.append(self.gateway.jvm.enumerate.Action.STAND_B)
        elif ((distance <= 150) and (my_state.equals(self.gateway.jvm.enumerate.State.AIR) or my_state.equals(self.gateway.jvm.enumerate.State.DOWN))
            and (((self.gameData.getStageWidth() - my_x) >= 200) or (xDifference > 0)) 
            and ((my_x >= 200) or xDifference < 0)):
            if energy >= 5:
                self.oppActions.append(self.gateway.jvm.enumerate.Action.AIR_DB)
            else:
                self.oppActions.append(self.gateway.jvm.enumerate.Action.AIR_B)
        else:
            self.oppActions.append(self.gateway.jvm.enumerate.Action.STAND_B)

    class Java:
        implements = ["aiinterface.AIInterface"]
