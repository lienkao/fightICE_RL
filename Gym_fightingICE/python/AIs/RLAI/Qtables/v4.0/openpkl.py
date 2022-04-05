import pickle
pickleFile = open('ZEN_v4.0.pkl', "rb")
QTables = pickle.load(pickleFile)
print(QTables)
