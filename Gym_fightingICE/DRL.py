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
sys.path.append('gym-figghtingice')
from python.AIs.StandAI import StandAI
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
        elif args[i] == "-d" or args[i] == "--d" or args[i] == "--done":
            global DONE_EPISODES
            DONE_EPISODES = int(args[i+1])
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
    # my hp energy x y, opp hp energy x y 
    valid_states = [0, 1, 2, 3, 65, 66, 67, 68]
    
    # n_states = env.observation_space.shape[0]
    n_states = len(valid_states)

    # print(n_actions)
    # Hyper parameters
    n_hidden = 50
    batch_size = 1024
    learning_rate = 0.1                 # learning rate
    epsilon = 0.2            #  epsilon-greedy
    discount_factor = 0.5              # reward discount factor
    target_replace_iter = 100 # target network 更新間隔
    memory_capacity = 10800
    n_episodes = 500
    
    dqn = DQN(n_states, n_actions, n_hidden, batch_size, learning_rate, epsilon, discount_factor, target_replace_iter, memory_capacity, VERSION)
    dqn.restore_params()
    state_freq = [0]*n_states
    for i_episode in range(DONE_EPISODES, n_episodes):
        # state = env.reset(p2=Machete)
        ori_state = env.reset(p2=StandAI)
        state = []
        for i in valid_states:
            state.append(ori_state[i])
        print("reset")
        cnt = 0
        steps = 0
        rewards = 0
        while True:
            # action = random.randint(0, 55)
            action = dqn.choose_action(state)
            ori_state, reward, done, _ = env.step(action)
            
            new_state = []
            for i in valid_states:
                new_state.append(ori_state[i])
            # print(new_state)
            rewards += reward
            if reward != 0:
                print("reward: {}, rewards: {}".format(reward, rewards))
            steps += 1
            dqn.store_transition(state, action, reward, new_state)
            if dqn.memory_counter > memory_capacity:
                # print("learn()")
                dqn.learn()
            if done:
                print('steps:',steps)
                cnt += 1	
                if cnt == 3:break
                ori_state = env.reset(p2=StandAI)
                state = []
                for i in valid_states:
                    state.append(ori_state[i])
                print("reset")
                done = False
                steps = 0
            state = new_state
        with open('./DRL/DRL_pkl/{}/test_gym_memory_{}.pkl'.format(VERSION, i_episode), 'wb+') as f:
            pickle.dump(dqn.memory, f)
        with open('./DRL/DRL_pkl/{}/net_{}.pkl'.format(VERSION, i_episode), 'wb+') as f:
            pickle.dump(dqn.eval_net, f)  
        dqn.save_params()
        print(list(dqn.eval_net.parameters()))   
        with open('./DRL/records/{}.txt'.format(VERSION), 'a+') as f:
            f.write("episodes {} finish, rewards: {}\n".format(i_episode, rewards))

    env.close()
    print('env close')

args = sys.argv
argc = len(args)
VERSION = 'v0.0'
OPPO_AI = "Machete"
DONE_EPISODES = 0
if __name__ == "__main__":
    check_args(args)
    print(f"version: {VERSION}")
    main()