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
from python.AIs.StandAI import StandAI
from python.AIs.ForwardAI import ForwardAI
from python.AIs.machete import Machete

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
    env = gym.make("FightingiceDataFrameskip-v0", java_env_path="",port=4242, freq_restart_java=10)
    
    

    # # Environment parameters
    n_actions = env.action_space.n
    # my hp energy x y, opp hp energy x y 
    # valid_states = [0, 1, 2, 3, 65, 66, 67, 68]
    
    n_states = env.observation_space.shape[0]

    # print(n_actions)
    # Hyper parameters
    n_hidden = 256
    batch_size = 128
    learning_rate = 0.1                 # learning rate
    epsilon = 0.2            #  epsilon-greedy
    discount_factor = 0.5              # reward discount factor
    target_replace_iter = 100 # target network 更新間隔
    memory_capacity = 1024
    n_episodes = 500
    dqn = DQN(n_states, n_actions, n_hidden, batch_size, learning_rate, epsilon, discount_factor, target_replace_iter, memory_capacity, VERSION)
    dqn.restore_params()
    # _actions = "AIR_B CROUCH_B STAND_B CROUCH_FB CROUCH_FA STAND_D_DB_BB DASH BACK_STEP".split()
    _actions = ['FOR_JUMP _B B B', 'FOR_JUMP', 'STAND_D_DF_FC', 'STAND_D_DB_BB', 'STAND_F_D_DFA', '6 6 6', 'B', 'AIR_DB']
    action_hit_damage = [20, 0, 120, 25, 10, 0, 10, 10]
    state_freq = [0]*n_states
    for i_episode in range(DONE_EPISODES, n_episodes):
        state = env.reset(p2=Machete)
        # state = env.reset(p2=ForwardAI)
        print("reset")
        cnt = 0
        steps = 0
        rewards = 0
        while True:
            # action = random.randint(0, 55)
            action = dqn.choose_action(state)
            print(f"action: {_actions[action]}")
            new_state, reward, done, _ = env.step(action)
            if reward == 0:
                reward -= action_hit_damage[action] / 10
            rewards += reward
            print(f"reward: {reward}, rewards: {rewards}")
            steps += 1
            dqn.store_transition(state, action, reward, new_state)
            if dqn.memory_counter > memory_capacity:
                # print("learn()")
                dqn.learn()
            if done:
                cnt += 1	
                with open('./DRL/records/{}.txt'.format(VERSION), 'a+') as f:
                    f.write("episodes {} round {} finish, rewards: {} steps: {}\n".format(i_episode, cnt, rewards, steps))
                if cnt == 3:break
                state = env.reset(p2=Machete)
                rewards = 0
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