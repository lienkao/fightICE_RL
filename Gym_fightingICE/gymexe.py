import gym
import gym_fightingice
import random
import numpy as np
import pickle

env = gym.make("FightingiceDataNoFrameskip-v0", java_env_path="",port=4243, freq_restart_java=1)

state = env.reset()
done = False
cnt = 0
steps = 0
memory_counter = 0
n_states = env.observation_space.shape[0]
n_actions = env.action_space.n
memory = np.zeros((10800, n_states * 2 + 2))
rewards = 0


while True:
	if not done:
		action = random.randint(0, 55)
		new_state, reward, done, _ = env.step(action)
		steps += 1
		rewards += reward
		print(reward)
		print('rewards: ', rewards)
		store_transition(state, action, reward, new_state, memory_counter)
		memory_counter += 1
	elif done:
		print('steps:',steps)
		print('rewards: ', rewards)
		cnt += 1	
		if cnt == 3:break
		state = env.reset()
		done = False
		steps = 0
	#print(new_obs)
print('final rewards', rewards)
pickleFile = open('test_gym_memory.pkl', 'wb+')
pickle.dump(memory, pickleFile)
pickleFile.close()

print("finish")

env.close()
print('close')
