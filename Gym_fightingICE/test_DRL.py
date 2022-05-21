import gym
import gym_fightingice
import sys
import random
import numpy as np
import pickle
import torch
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
        elif args[i] == "--port":
            global PORT
            PORT = int(args[i+1])
      
def main():
    env = gym.make("FightingiceDataNoFrameskip-v0", java_env_path="",port=PORT, freq_restart_java=10)
    
    

    # # Environment parameters
    n_actions = env.action_space.n
    n_states = env.observation_space.shape[0]
    # print(n_actions)
    # Hyper parameters
    n_hidden = 50
    batch_size = 32
    learning_rate = 0.0                # learning rate
    epsilon = 0.1            #  epsilon-greedy
    discount_factor = 0.5              # reward discount factor
    target_replace_iter = 100 # target network 更新間隔
    memory_capacity = 10800
    n_episodes = 30
    done_episodes = 0
    dqn = DQN(n_states, n_actions, n_hidden, batch_size, learning_rate, epsilon, discount_factor, target_replace_iter, memory_capacity, VERSION)
    dqn.restore_params()
    for i_episode in range(done_episodes, n_episodes):
        # state = env.reset(p2=Machete)
        state = env.reset()
        print("reset")
        cnt = 0
        steps = 0
        rewards = 0
        while True:
            # action = random.randint(0, 55)
            action = dqn.choose_action(state)
            new_state, reward, done, _ = env.step(action)
            # print(new_state)
            rewards += reward
            # if reward != 0:
            #     print("reward: {}, rewards: {}".format(reward, rewards))
            steps += 1
            if done:
                # print('steps:',steps)
                cnt += 1	
                if cnt == 3:break
                state = env.reset()
                # print("reset")
                done = False
                steps = 0
            state = new_state
              
        with open('./DRL/records/{}_test.txt'.format(VERSION), 'a+') as f:
            f.write("episodes {} finish, rewards: {}\n".format(i_episode, rewards))

    env.close()
    print('env close')

args = sys.argv
argc = len(args)
VERSION = 'v0.0'
OPPO_AI = "Machete"
PORT = 4242
if __name__ == "__main__":
    check_args(args)
    print(f"version: {VERSION}")
    main()