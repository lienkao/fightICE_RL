import pickle
pickleFile = open('ZEN_v2.0.pkl', "rb")
QTables = pickle.load(pickleFile)
print(QTables)
