#!/bin/bash
/usr/bin/tmux send-keys -t "0:1" C-z 'cd ~/mapPi' Enter 'python ~/mapPi/nbaMap.py' Enter
