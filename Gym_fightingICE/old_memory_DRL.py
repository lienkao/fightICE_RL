import gym
import gym_fightingice
import sys
import random
import numpy as np
import pickle
import torch
import os
from torch import nn
from DQN import DQN
from DQN import Net
sys.path.append('gym-fightingice')
from gym_fightingice.envs.Machete import Machete
def check_args(args):
    for i in range(argc):
        # if args[i] == "-n" or args[i] == "--n" or args[i] == "--number":
        #     global GAME_NUM
        #     GAME_NUM = int(args[i+1])
        if args[i] == "-o" or args[i] == "--o" or args[i] == "--opponent":
            global OPPO_AI
            OPPO_AI = args[i+1]
        elif args[i] == "-v" or args[i] == "--v" or args[i] == "--version":
            global VERSION
            VERSION = args[i+1]
        # elif args[i] == "-m" or args[i] == "--m" or args[i] == "--mode":
        #     global TRAIN_MODE
        #     if args[i+1] == "train":
        #         TRAIN_MODE = True
        #     elif args[i+1] == "test":
        #         TRAIN_MODE = False
      
def main():
    env = gym.make("FightingiceDataNoFrameskip-v0", java_env_path="",port=4242, freq_restart_java=10)
    
    

    # # Environment parameters
    n_actions = env.action_space.n
    n_states = env.observation_space.shape[0]
    # print(n_actions)
    # Hyper parameters
    n_hidden = 50
    batch_size = 1080
    learning_rate = 0.1                 # learning rate
    epsilon = 0.1            #  epsilon-greedy
    discount_factor = 0.5              # reward discount factor
    target_replace_iter = 100 # target network 更新間隔
    memory_capacity = 10800
    n_episodes = 100
    done_episodes = 0
    data_amount = 100
    data_version = 'v3.1'
    dqn = DQN(n_states, n_actions, n_hidden, batch_size, learning_rate, epsilon, discount_factor, target_replace_iter, memory_capacity, VERSION)
    dqn.restore_params()
    data_folder = f'./DRL/DRL_pkl/{data_version}/'
    for file in os.listdir(data_folder):
        with open(os.path.join(data_folder, file), 'rb+') as f:
            dqn.memory = pickle.load(f)
            for i in range(2100):
                dqn.learn()
                dqn.save_params()   

    env.close()
    print('env close')

args = sys.argv
argc = len(args)
VERSION = 'v0.0'
OPPO_AI = "Machete"

if __name__ == "__main__":
    check_args(args)
    print(f"version: {VERSION}")
    main()
