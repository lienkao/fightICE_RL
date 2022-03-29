import gym
import sys
from mcts_general.agent import MCTSAgent
from mcts_general.config import MCTSAgentConfig
from mcts_general.game import DiscreteGymGame

sys.path.append('gym-fightingice')
from gym_fightingice.envs.Machete import Machete

def main():
    config = MCTSAgentConfig()
    config.num_simulations = 1
    agent = MCTSAgent(config)
    game = DiscreteGymGame(env = gym.make("FightingiceDataNoFrameskip-v0", java_env_path="", port=4242))
    state = game.reset()
    done = False
    reward = 0
    while not done:
        action = agent.step(game, state, reward, done)
        state, reward, done = game.step(action)
    game.close()

if __name__ == "__main__":
    main()
