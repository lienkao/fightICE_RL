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

env = gym.make("FightingiceDataNoFrameskip-v0", java_env_path="",port=4242, freq_restart_java=10)
    
    

# # Environment parameters
n_actions = env.action_space.n
n_states = env.observation_space.shape[0]
# print(n_actions)
# Hyper parameters
n_hidden = 50
batch_size = 32
learning_rate = 0.1                 # learning rate
epsilon = 0.1            #  epsilon-greedy
discount_factor = 0.5              # reward discount factor
target_replace_iter = 100 # target network 更新間隔
memory_capacity = 10800
n_episodes = 500
done_episodes = 497
dqn = DQN(n_states, n_actions, n_hidden, batch_size, learning_rate, epsilon, discount_factor, target_replace_iter, memory_capacity, 'v4.0')
dqn.restore_params()
print(list(dqn.eval_net.parameters()))