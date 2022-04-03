import pickle
pickleFile = open('ZEN_v2.0.plk', "rb")
QTables = pickle.load(pickleFile)
print(QTables)
