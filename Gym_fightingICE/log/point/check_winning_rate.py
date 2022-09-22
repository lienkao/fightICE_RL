from cProfile import label
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import csv
import os

# get all file in this folder
allFileList = os.listdir('./')

roundCnt = 0
gameCnt = 0
winPerGameCnt = 0
losePerGameCnt = 0
winPer100Game = 0

per100GameWinRate = []
everyGameWinCnt = []
everyGameLoseCnt = []

for file in allFileList:
    # check if it is .csv file
    if '.csv' in file:
        # open csv file
        with open(file, newline='') as csvfile:
            rows = csv.reader(csvfile)
            # check if the round is win
            for row in rows:
                roundCnt += 1
                if row[1] > row[2]:
                    winPerGameCnt += 1
                elif row[2] > row[1]:
                    losePerGameCnt -= 1
            # 3 rounds over 
            if roundCnt % 3 == 0:
                gameCnt += 1
                everyGameWinCnt.append(winPerGameCnt)
                everyGameLoseCnt.append(losePerGameCnt)
                winPer100Game += winPerGameCnt
                winPerGameCnt = 0
                losePerGameCnt = 0
            # 100 games over
            if gameCnt % 100 == 0:
                per100GameWinRate.append(winPer100Game / 300)
                winPer100Game = 0

if gameCnt % 100 != 0:
    per100GameWinRate.append(winPer100Game / (gameCnt % 100 * 3))
                
plt.bar([i for i in range(1, gameCnt+1)], everyGameWinCnt, align='center', color = 'blue')
plt.bar([i for i in range(1, gameCnt+1)], everyGameLoseCnt, align='center', color = 'red')
plt.show()
print(max(per100GameWinRate))
plt.plot([i for i in range(1, len(per100GameWinRate)+1)], per100GameWinRate)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False
plt.ylabel("每一百場的平均勝率")                
plt.xlabel("場數（單位：百）")
plt.show()