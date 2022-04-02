import pickle
pickleFile = open('ZEN_v2.0_record.plk', "rb")
QTables = pickle.load(pickleFile)
print(QTables)
