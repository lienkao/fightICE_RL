import os
import shutil
from datetime import datetime

class Record():
    def __init__(self, variable_folder, OPPO_AI, PREDICT_OPPO, GAME_NUM, log_folder_path = '../log/point'):
        self.log_folder_path = log_folder_path
        self.variable_folder = variable_folder
        self.log_variable_path = os.path.join(self.log_folder_path, self.variable_folder)
        self.OPPO_AI = OPPO_AI
        self.PREDICT_OPPO = PREDICT_OPPO
        self.GAME_NUM = GAME_NUM

    def organize_log(self):
        print(self.log_variable_path)
        
        if not os.path.isdir(self.log_variable_path):
            os.mkdir(self.log_variable_path)
        self.record()
        for log in os.listdir(self.log_folder_path):
            if log.endswith(".csv"):
                print(os.path.join(self.log_variable_path, log))
                shutil.move(os.path.join(self.log_folder_path, log), os.path.join(self.log_variable_path, log))

    def record(self):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            file_path = os.path.join(self.log_variable_path, self.variable_folder + '.txt')
            # print(file_path)
            f = open(file_path, 'a+')
            f.write(current_time)
            f.write('\n')
            f.write('GAME_NUM: ' + str(self.GAME_NUM))
            f.write('\n')
            f.write('OPPO_AI: ' + self.OPPO_AI)
            f.write('\n')
            f.write('PREDICT_OPPO: ' + self.PREDICT_OPPO)
            f.write('\n')
            f.close()
