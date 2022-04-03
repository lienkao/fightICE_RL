import pickle
pickleFile = open('ZEN_v3.0.pkl', "rb")
QTables = pickle.load(pickleFile)
print(QTables)
