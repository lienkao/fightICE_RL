import torch
from torchviz import make_dot
from DQN import DQN
from DQN import Net
import gym
import gym_fightingice
env = gym.make("FightingiceDataNoFrameskip-v0", java_env_path="",port=4243, freq_restart_java=10)
    
    

# # Environment parameters
n_actions = env.action_space.n
n_states = env.observation_space.shape[0]
# Hyper parameters
n_hidden = 50
batch_size = 32
learning_rate = 0.1                 # learning rate
epsilon = 0.1            #  epsilon-greedy
discount_factor = 0.5              # reward discount factor
target_replace_iter = 100 # target network 更新間隔
memory_capacity = 10800
n_episodes = 600
done_episodes = 447
VERSION = 'v2.0'
dqn = DQN(n_states, n_actions, n_hidden, batch_size, learning_rate, epsilon, discount_factor, target_replace_iter, memory_capacity, VERSION)
dqn.restore_params()
make_dot(dqn).render("attached", format="png")