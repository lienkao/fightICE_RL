from typing import final
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pickle

def getData(table):
    data = []
    for x in table:
        for y in x:
            for bound in y:
                data.append(bound[4])
                # for power in bound:
                #     data.append(power)
    return data

version = input('Version: (vX.X.X): ')

filePath = './{}/ZEN_{}_record.pkl'.format(version, version)
finalFilePath = './{}/ZEN_{}.pkl'.format(version, version)

pickleFile = open(filePath, 'rb')
finalPickleFile = open(finalFilePath, 'rb')

Qtable = pickle.load(pickleFile)
FQtable = pickle.load(finalPickleFile)

max = FQtable.max()
min = FQtable.min()

finalPickleFile.close()

fig = plt.figure()
# plt.title('heatmap')
# plt.xlabel('actions')
# plt.xticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5], ['STAND_B', 'CROUCH_B', 'CROUCH_FB', 'STAND_D_DB_BB', 'STAND_D_DF_FB', 'STAND_D_DF_FC',
#             'STAND_D_DB_BA', 'AIR_B', 'AIR_DB', 'AIR_D_DF_FB', 'AIR_UB', 'AIR_F_D_DFB'], rotation = 'vertical', fontsize = 8)
# plt.ylabel('states')


data = getData(Qtable)
ax = sns.heatmap(data, yticklabels = False, center = 0, vmax = max, vmin = min)

def init():
    plt.clf()
    ax = sns.heatmap(data, yticklabels = False, center = 0, vmax = max, vmin = min)

def animate(i):
    plt.clf()
    Qtable = pickle.load(pickleFile)
    data = getData(Qtable)
    ax = sns.heatmap(data, yticklabels = False, center = 0, vmax = max, vmin = min)

anim = animation.FuncAnimation(fig, animate, init_func = init, interval = 50)

plt.show()

pickleFile.close()