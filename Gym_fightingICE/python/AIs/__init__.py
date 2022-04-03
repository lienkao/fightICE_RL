import imp
import sys
import os
# add AI path to sys.path
sys.path.append(os.path.dirname(__file__))  # noqa: E402
from .ForwardAI import ForwardAI
from .KickAI import KickAI
from .MctsAi import MctsAi
from .SkillAI import SkillAI
from .machete import Machete
from .RLAI.RLAI import RLAI
from .RLAI.RLAI_train import RLAI_train