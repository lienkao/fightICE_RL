import sys
from time import sleep
import math
from py4j.java_gateway import JavaGateway, GatewayParameters, CallbackServerParameters, get_field
from DisplayInfo import DisplayInfo
import logging
import AIs
import os
import shutil
from datetime import datetime
def check_args(args):
    for i in range(argc):
        if args[i] == "-n" or args[i] == "--n" or args[i] == "--number":
            global GAME_NUM
            GAME_NUM = int(args[i+1])
        elif args[i] == "-o" or args[i] == "--o" or args[i] == "--opponent":
            global OPPO_AI
            OPPO_AI = args[i+1]
        elif args[i] == "-v" or args[i] == "--v" or args[i] == "--version":
            global VERSION
            VERSION = args[i+1]
        elif args[i] == "-m" or args[i] == "--m" or args[i] == "--mode":
            global TRAIN_MODE
            if args[i+1] == "train":
                TRAIN_MODE = True
            elif args[i+1] == "test":
                TRAIN_MODE = False
        elif args[i] == "-e" or args[i] == "--e" or args[i] == "--epsilon":
            global EPSILON
            EPSILON = float(args[i+1])
        elif args[i] == "--lr" or args[i] == "--learningRate":
            global LEARNING_RATE
            LEARNING_RATE = float(args[i+1])
        elif args[i] == "--fr" or args[i] == "--futureRate":
            global FUTURE_RATE
            FUTURE_RATE = float(args[i+1])
def start_game():
        print("version: {}, Train Mode: {}".format(VERSION, TRAIN_MODE))
        if TRAIN_MODE:
            print("epsilon: {}, learning Rate: {}, future Rate: {}".format(EPSILON, LEARNING_RATE, FUTURE_RATE))
        p1 = AIs.RLAI(gateway, "./AIs/RLAI/Qtables", VERSION, TRAIN_MODE, EPSILON, LEARNING_RATE, FUTURE_RATE)
        p2 = eval(('AIs.' + OPPO_AI))(gateway)
        manager.registerAI(p1.__class__.__name__, p1)
        manager.registerAI(p2.__class__.__name__, p2)
        print("Start game", "game: {}".format(GAME_NUM))
        game = manager.createGame("ZEN", "ZEN",
                                  p1.__class__.__name__,
                                  p2.__class__.__name__,
                                  GAME_NUM)
        manager.runGame(game)

        print("After game")
        sys.stdout.flush()

def close_gateway():
    sleep(5)
    print("close_callback_sever")
    gateway.close_callback_server()
    sleep(5)
    print("close")
    gateway.close()


def main_process(): 
    check_args(args)
    start_game()
    close_gateway()

args = sys.argv
argc = len(args)
VERSION = 'v0.0'
TRAIN_MODE = True
GAME_NUM = 1
OPPO_AI = "Machete"
EPSILON = 0.9
LEARNING_RATE = 0.1
FUTURE_RATE = 0.1
gateway = JavaGateway(gateway_parameters=GatewayParameters(port=4242), callback_server_parameters=CallbackServerParameters())
manager = gateway.entry_point

main_process()

