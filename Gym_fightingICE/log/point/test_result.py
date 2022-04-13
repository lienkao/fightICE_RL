import os
from matplotlib import pyplot as plt

def main(folder_path):
    data = []
    for fname in os.listdir(folder_path):
        if '.csv' not in fname: continue
        with open(os.path.join(folder_path, fname)) as infile:
            for line in infile:
                #print(line)
                if len(line)==0: break
                line = line.split(',')
                data.append([fname, line[1], line[2]])

    data.sort(key = lambda x: x[0])
    for row in data:
        print(row)



    score = []
    cnt = 0
    for row in data:
        if float(row[2]) < float(row[1]):
            cnt += 1
        score.append(float(row[2])/(float(row[1])+float(row[2])))
    print(cnt)
    plt.hist(score)
    plt.title(folder_path)
    plt.savefig(os.path.join(folder_path, 'result'))
    # plt.show()
    plt.clf()
    '''
    with open('tcc.csv', 'w') as outfile:
        for row in data:
            outfile.write(','.join(row)+'\n')
    '''
if __name__ == '__main__':

    # for folder in os.listdir():
    #     if 'Test' in folder:
    #         main(folder)

    version = input('Version: (vX.X.X)')
    folder_path = 'RL_Test_{}'.format(version)
    main(folder_path)
