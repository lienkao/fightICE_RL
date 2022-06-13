import os
import numpy as np
from matplotlib import pyplot as plt

data = []
Date = input('Date: (vX.X.X)')
folder_path = './{}'.format(Date)
for fname in os.listdir(folder_path):
    if 'Mach' not in fname: continue
    with open(os.path.join(folder_path, fname)) as infile:
        for line in infile:
            #print(line)
            if len(line)==0: break
            line = line.split(',')
            data.append([fname, line[1], line[2]])

data.sort(key = lambda x: x[0])
for row in data:
    print(row)



p2hp = []
p1hp = []
cnt = 0
x = np.arange(len(data))
for row in data:
    p1 = int(row[1])
    p2 = int(row[2])
    if p1 > p2:
        p1hp.append(int(row[1]))
        p2hp.append(0)
    elif p1 == p2:
        p1hp.append(0)
        p2hp.append(0)
    else:
        p1hp.append(0)
        p2hp.append(-int(row[2]))

plt.bar(x, p1hp)
plt.bar(x, p2hp)
plt.show()
'''
with open('tcc.csv', 'w') as outfile:
    for row in data:
        outfile.write(','.join(row)+'\n')
'''
