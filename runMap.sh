#!/bin/bash
/usr/bin/tmux send-keys -t "0:1.1" C-C C-L " cd /home/jlc/mapPi" C-m " ./map.py mlb" C-m
/usr/bin/tmux send-keys -t "0:1.2" C-C C-L " cd /home/jlc/mapPi" C-m " ./map.py nfl" C-m 
/usr/bin/tmux send-keys -t "0:1.3" C-C C-L " cd /home/jlc/mapPi" C-m " ./map.py nba" C-m
