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

def main():
    env = gym.make("FightingiceDataFrameskip-v0", java_env_path="",port=4242, freq_restart_java=1)
    
    

    # # Environment parameters
    n_actions = env.action_space.n
    n_states = env.observation_space.shape[0]

    # Hyper parameters
    n_hidden = 50
    batch_size = 32
    lr = 0.1                 # learning rate
    epsilon = 0.9            #  epsilon-greedy
    gamma = 0.5              # reward discount factor
    target_replace_iter = 100 # target network 更新間隔
    memory_capacity = 10800
    n_episodes = 300

    dqn = DQN(n_states, n_actions, n_hidden, batch_size, lr, epsilon, gamma, target_replace_iter, memory_capacity)

    for i_episode in range(n_episodes):
        # state = env.reset(p2=Machete)
        state = env.reset()
        print("reset")
        cnt = 0
        steps = 0
        while True:
            action = random.randint(0, 55)
            new_state, reward, done, _ = env.step(action)
            steps += 1
            dqn.store_transition(state, action, reward, new_state)
            if done:
                print('steps:',steps)
                cnt += 1	
                if cnt == 3:break
                state = env.reset()
                print("reset")
                done = False
                steps = 0
            state = new_state

        pickleFile = open('./DRL_pkl/test_gym_memory_{}.pkl'.format(i_episode), 'wb+')
        pickle.dump(dqn.memory, pickleFile)
        pickleFile.close()

        print("episodes {} finish".format(i_episode))

    env.close()
    print('env close')
        



if __name__ == "__main__":
    main()