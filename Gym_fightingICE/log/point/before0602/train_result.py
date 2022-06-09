import os
from matplotlib import pyplot as plt

data = []
version = input('Version: (vX.X.X)')
folder_path = './RL_test_{}'.format(version)
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



y = []
cnt = 0
for row in data:
    y.append(float(row[2]) / (float(row[2]) + float(row[1])))
plt.plot(y)
plt.show()
'''
with open('tcc.csv', 'w') as outfile:
    for row in data:
        outfile.write(','.join(row)+'\n')
'''
