import sys
from time import sleep
import math
from py4j.java_gateway import JavaGateway, GatewayParameters, CallbackServerParameters, get_field

from DisplayInfo import DisplayInfo
from AIs.Node import Node
import AIs

def check_args(args):
	for i in range(argc):
		if args[i] == "-n" or args[i] == "--n" or args[i] == "--number":
			global GAME_NUM
			GAME_NUM = int(args[i+1])

def start_game():
        #p1 = TestAi(gateway)
        p1 = AIs.KickAI(gateway)
        p2 = AIs.Machete-(gateway)
        manager.registerAI(p1.__class__.__name__, p1)
        manager.registerAI(p2.__class__.__name__, p2)
        print("Start game")

        game = manager.createGame("ZEN", "ZEN",
                                  p1.__class__.__name__,
                                  p2.__class__.__name__,
                                  GAME_NUM)
        manager.runGame(game)

        print("After game")
        sys.stdout.flush()

def close_gateway():
	gateway.close_callback_server()
	gateway.close()

def main_process(): 
	check_args(args)
	start_game()
	close_gateway()

args = sys.argv
argc = len(args)
GAME_NUM = 5
gateway = JavaGateway(gateway_parameters=GatewayParameters(port=4242), callback_server_parameters=CallbackServerParameters());
manager = gateway.entry_point

main_process()

