import pickle
pickleFile = open('ZEN_v2.1.pkl', "rb")
cnt = 0
try:
    while True:
        QTables = pickle.load(pickleFile)
        cnt += 1
except:
    pass


print(QTables)
