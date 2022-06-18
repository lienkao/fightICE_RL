
from tracemalloc import is_tracing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
import sys
def check_args(args):
    for i in range(argc):
        # if args[i] == "-n" or args[i] == "--n" or args[i] == "--number":
        #     global GAME_NUM
        #     GAME_NUM = int(args[i+1])
        if args[i] == "-v" or args[i] == "--v" or args[i] == "--version":
            global VERSION
            VERSION = args[i+1]
        elif args[i] == "-p" or args[i] == "--p" or args[i] == "--poly":
            global POLY_N
            POLY_N = int(args[i+1])
        # elif args[i] == "-m" or args[i] == "--m" or args[i] == "--mode":
        #     global TRAIN_MODE
        #     if args[i+1] == "train":
        #         TRAIN_MODE = True
        #     elif args[i+1] == "test":
        #         TRAIN_MODE = False
def poly(rewards, type, is_tracking = False):
    episodes = [x for x in range(len(rewards))]
    # 
    # model=linear_model.LinearRegression()
    # model.fit(X,y)
    regr=make_pipeline(PolynomialFeatures(POLY_N),linear_model.LinearRegression())
    regr.fit(np.reshape(episodes, (len(episodes), 1)), np.reshape(rewards, (len(rewards), 1)))

    plt.title(f"version: {VERSION} {type}")
    plt.scatter(episodes,rewards)
    plt.plot(episodes, regr.predict(np.reshape(episodes, (len(episodes), 1))), color='blue', linewidth=3)
    # plt.plot(X, regr.predict(X),color='blue',linewidth=1)
    # plt.plot(X,model.predict(X))
    if is_tracking:
        plt.draw()
        plt.pause(0.5)
        plt.clf()
    else:
        plt.show()
def get_rewards():
    rewards = []
    with open(f"{VERSION}.txt", 'r') as f:
        t = f.read().split('\n')
        # print(t)
        for row in t:
            if row == '':continue
            cols = row.split()
            for i, col in enumerate(cols):
                if 'reward' in col:
                    rewards.append(float(cols[i+1]))
            
    return rewards
def get_steps():
    rewards = []
    with open(f"{VERSION}.txt", 'r') as f:
        t = f.read().split('\n')
        # print(t)
        for row in t:
            if row == '':continue
            cols = row.split()
            for i, col in enumerate(cols):
                if 'steps' in col:
                    rewards.append(float(cols[i+1]))
            
    return rewards
# for test
def show_test():
    scores = []
    plt.figure()
    plt.subplot(1, 3, 1)
    with open("v3.0_test.txt", 'r') as f:
        t = f.read().split('\n')
        # print(t)
        for row in t:
            if row == '':continue
            cols = row.split()
            scores.append(int(cols[4]))
    plt.title("version: v3.0 test result")
    plt.hist(scores)
    print("v3.0 test mean",np.mean(scores))
    print("v3.0 test std",np.std(scores))
    scores = []
    plt.subplot(1, 3, 2)
    with open("v3.1_one_train_test.txt", 'r') as f:
        t = f.read().split('\n')
        # print(t)
        for row in t:
            if row == '':continue
            cols = row.split()
            scores.append(int(cols[4]))
    plt.title("version: v3.1 one train test result")
    plt.hist(scores)
    print("v3.1 one train test mean", np.mean(scores))
    print("v3.1 one train test std", np.std(scores))
    scores = []
    plt.subplot(1, 3, 3)
    with open("v3.1_test.txt", 'r') as f:
        t = f.read().split('\n')
        # print(t)
        for row in t:
            if row == '':continue
            cols = row.split()
            scores.append(int(cols[4]))
    plt.title("v3.1 test result")
    plt.hist(scores)
    print("v3.1 test mean", np.mean(scores))
    print("v3.1 test std", np.std(scores))
    plt.show()
    return scores
def show_all_point(rewards):
    plt.title(f"version: {VERSION}")
    plt.plot([x for x in range(len(rewards))], rewards, 'bo')
    plt.show()

def fix_record_episodes():
    with open(f"{VERSION}.txt", 'r+') as r:
        with open(f"{VERSION}_repair.txt", 'w+') as w:
            t = r.read().split('\n')
            repeat=False
            exist=set()
            index = 0
            for row in t:
                if row == '':continue
                cols = row.split()
                if cols[1] in exist:
                    cols[1] = str(index)
                exist.add(cols[1])
                index += 1
                w.write(' '.join(cols)+'\n')
def keep_track_game():
    while True:
        rewards = get_rewards()
        poly(rewards, is_tracking=True)
args = sys.argv
argc = len(args)
VERSION = 'v0.0'
POLY_N = 1


if __name__ == "__main__":
    
    check_args(args)
    # keep_track_ga
    # me()
    rewards = get_rewards()
    poly(rewards[:450], 'rewards')
    steps = get_steps()
    poly(steps[:450], 'steps')
    
