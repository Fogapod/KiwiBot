#!/bin/bash

while true; do
    python3 main.py
    
    if [ $? == 2 ];
    then
        echo "Terminate exit code recieved. Exiting"
        break
    fi

    # git reset --hard
    git pull origin master

    for second in {10..1}
    do
        echo -ne "Restarting in $second seconds..\r"
        sleep 1
    done
done
