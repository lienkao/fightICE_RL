import pickle
pickleFile = open('ZEN.pkl', "rb")
QTables = pickle.load(pickleFile)
print(QTables)
