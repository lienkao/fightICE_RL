import os

print("Please enter the version code (ex: v8.2):", end = '')
version = input()

filename = version + ".txt"

f = open(filename, 'r')
lines = f.readlines()
# 當前 episodes
max_episodes = 0
# 修改後的資料
renumber_lines = []

for line in lines:
    now = line.split()
    if len(now) > 2:
        if max_episodes > int(now[1]):
            if int(now[3]) == 1:
                max_episodes += 1
            
            # 重新組成
            new_str = now[0]+" "+str(max_episodes)+" "+now[2]+" "+now[3]+" "+now[4]+" "+now[5]+" "+now[6]+" "+now[7]+" "+now[8]+"\n"
            renumber_lines.append(new_str)
        else:
            max_episodes = int(now[1])
            renumber_lines.append(line)
        
f.close()

f = open(filename, 'w')
f.writelines(renumber_lines)
f.close()