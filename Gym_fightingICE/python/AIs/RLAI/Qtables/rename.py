import os
name = {"v4.1.0": "v4.1", 
        "v4.1.1": "v4.2",
        "v4.1.2": "v4.3",
        "v4.1.3": "v4.4",
        "v4.1.4": "v4.5",
        "v4.1.7": "v4.5.1",
        "v4.1.5": "v4.6",
        "v4.1.6": "v4.7"}
for folder_name in os.listdir():
    for old_version in name.values():
        if old_version in folder_name:
             for file_name in os.listdir(folder_name):
                if 'record' in file_name:
                    os.rename(os.path.join(folder_name, file_name), os.path.join(folder_name, file_name[:-17] + name[old_version] + '_record' + '.pkl'))
                else:
                    os.rename(os.path.join(folder_name, file_name), os.path.join(folder_name, file_name[:-10] + name[old_version] + '.pkl'))