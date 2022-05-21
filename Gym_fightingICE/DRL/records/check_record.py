
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
def poly(rewards):
    episodes = [x for x in range(len(rewards))]
    # 
    # model=linear_model.LinearRegression()
    # model.fit(X,y)
    regr=make_pipeline(PolynomialFeatures(POLY_N),linear_model.LinearRegression())
    regr.fit(np.reshape(episodes, (len(episodes), 1)), np.reshape(rewards, (len(rewards), 1)))

    plt.title(f"version: {VERSION}")
    plt.scatter(episodes,rewards)
    plt.plot(episodes, regr.predict(np.reshape(episodes, (len(episodes), 1))), color='blue', linewidth=3)
    # plt.plot(X, regr.predict(X),color='blue',linewidth=1)
    # plt.plot(X,model.predict(X))
    plt.show()
def get_rewards():
    rewards = []
    with open(f"{VERSION}.txt", 'r') as f:
        t = f.read().split('\n')
        # print(t)
        for row in t:
            if row == '':continue
            cols = row.split()
            rewards.append(int(cols[4]))
    return rewards
# for test
def show_test():
    scores = []
    with open(f"{VERSION}_test.txt", 'r') as f:
        t = f.read().split('\n')
        # print(t)
        for row in t:
            if row == '':continue
            cols = row.split()
            scores.append(int(cols[4]))
    plt.title(f"version: {VERSION} test result")
    plt.hist(scores)
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

args = sys.argv
argc = len(args)
VERSION = 'v0.0'
POLY_N = 1
        
if __name__ == "__main__":
    check_args(args)
    # fix_record_episodes()
    # rewards = get_rewards()
    show_test()
    # poly(rewards)

    