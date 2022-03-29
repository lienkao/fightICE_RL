from py4j.java_gateway import get_field

class SkillAI(object):
    def __init__(self, gateway):
        self.gateway = gateway
        
    def close(self):
        pass
        
    def getInformation(self, frameData, isControl):
        # Getting the frame data of the current frame
        self.frameData = frameData
        self.cc.setFrameData(self.frameData, self.player)
    # please define this method when you use FightingICE version 3.20 or later
    def roundEnd(self, x, y, z):
        # print(x)
        # print(y)
        # print(z)
        pass

    # please define this method when you use FightingICE version 4.00 or later
    def getScreenData(self, sd):
        pass
        
    def initialize(self, gameData, player):
        # Initializing the command center, the simulator and some other things
        self.inputKey = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.cc = self.gateway.jvm.aiinterface.CommandCenter()
            
        self.player = player
        self.gameData = gameData
        self.simulator = self.gameData.getSimulator()
        self.spSkill = self.gateway.jvm.enumerate.Action.STAND_D_DF_FC
        self.myMotion = self.gateway.jvm.java.util.ArrayList()
        self.myMotion = self.gameData.getMotionData(player)
        return 0
        
    def input(self):
        # Return the input for the current frame
        return self.inputKey

    def canProcessing(self):
        return ((not self.frameData.getEmptyFlag()) and (self.frameData.getRemainingTime() > 0))

    def processing(self):    
                  
        if self.cc.getSkillFlag():
            self.inputKey = self.cc.getSkillKey()
            return
        self.inputKey.empty()
        self.cc.skillCancel()  
        if self.canProcessing():
            # when energy enough then use skill
            energy = self.frameData.getCharacter(self.player).getEnergy()
            if abs(self.myMotion.get(self.gateway.jvm.enumerate.Action.valueOf(self.spSkill.name()).ordinal())
                .getAttackStartAddEnergy()) <= energy:
                # Just spam kick
                self.cc.commandCall(self.spSkill.name())
            else:
                self.cc.commandCall("BACK_STEP")
                        
    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]
        
