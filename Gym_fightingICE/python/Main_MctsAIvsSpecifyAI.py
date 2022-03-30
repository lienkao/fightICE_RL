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
from record import Record
def check_args(args):
    for i in range(argc):
        if args[i] == "-n" or args[i] == "--n" or args[i] == "--number":
            global GAME_NUM
            GAME_NUM = int(args[i+1])
        elif args[i] == "-d" or args[i] == "--d" or args[i] == "--depth":
            global UCT_TREE_DEPTH
            UCT_TREE_DEPTH = int(args[i+1])
        elif args[i] == "-o" or args[i] == "--o" or args[i] == "--opponent":
            global OPPO_AI
            OPPO_AI = args[i+1]
        elif args[i] == "-p" or args[i] == "--p" or args[i] == "--predict":
            global PREDICT_OPPO
            PREDICT_OPPO = args[i+1]


def start_game():
        p1 = AIs.RLAI(gateway, "/AIs/Qtables")
        p2 = eval(('AIs.' + OPPO_AI))(gateway)
        manager.registerAI(p1.__class__.__name__, p1)
        manager.registerAI(p2.__class__.__name__, p2)
        print("Start game", "depth: {}".format(UCT_TREE_DEPTH), "game: {}".format(GAME_NUM))
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

def organize_log():
    log_folder_path = '../log/point'
    depth_folder_path = 'UCT_TREE_DEPTH_' + str(UCT_TREE_DEPTH)
    log_depth_path = os.path.join(log_folder_path, depth_folder_path)
    if not os.path.isdir(log_depth_path):
        os.mkdir(log_depth_path)
    record(log_depth_path, UCT_TREE_DEPTH)
    for log in os.listdir(log_folder_path):
        if log.endswith(".csv"):
            shutil.move(log, os.path.join(log_depth_path, log))

def record(folder_path):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        file_path = os.path.join(folder_path, folder_path + '.txt')
        # print(file_path)
        f = open(file_path, 'w+')
        f.write(current_time)
        f.write('GAME_NUM: ' + str(GAME_NUM))
        f.write('OPPO_AI: ' + OPPO_AI)
        f.write('PREDICT_OPPO: ' + PREDICT_OPPO)
        f.close()

def main_process(): 
    check_args(args)
    start_game()
    close_gateway()
    r = Record('UCT_Tree_Depth' + str(UCT_TREE_DEPTH), OPPO_AI, PREDICT_OPPO, GAME_NUM)
    r.organize_log()

args = sys.argv
argc = len(args)
GAME_NUM = 3
UCT_TREE_DEPTH = 3
OPPO_AI = "ForwardAI"
PREDICT_OPPO = "ForwardAI"
gateway = JavaGateway(gateway_parameters=GatewayParameters(port=4242), callback_server_parameters=CallbackServerParameters());
manager = gateway.entry_point

main_process()

