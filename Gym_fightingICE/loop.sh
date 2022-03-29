#!/bin/bash
gnome-terminal --window -- ./run_stage.sh && sleep 2 && gnome-terminal --window -- python3 ./python/Main_MctsAIvsSpecifyAI.py -o $1 -p $2 -d $3 -n $4;exec bash


while true 
do
    monitor=`ps -ef | grep Main_MctsAIvsSpecifyAI.py | grep -v grep | wc -l ` 
    if [ "$monitor" == 0 ] 
    then
        echo "Main_MctsAIvsSpecifyAI.py is done"
        sleep 5
        ps -ef|grep run_stage.sh|grep -v grep|awk '{print $2}'|xargs kill -9
        echo "run_stage.sh program is running, and kill it"
        break
    # else 
    #     echo "Main_MctsAIvsSpecifyAI.py is running"
    fi
done
