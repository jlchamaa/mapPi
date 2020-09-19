#!/usr/bin/python
import subprocess
import re
import sys
import serial
import time
import datetime
from teams import teams, gamma


ser = serial.Serial('/dev/ttyACM0', 38400)

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def preciseApply(ledNum, r, g, b, flashes):
    ba = bytearray()
    ba[0:8] = [ledNum, flashes, gamma[r], gamma[g], gamma[b], gamma[r], gamma[g], gamma[b], 0]
    for index, value in enumerate(ba):
        #ensures zerobyte is the sole zero.  Adjust values back on Arduino Side!
        ba[index] = min(255, value+1)
    ba[8] = int(0)
    ser.write(ba)


def application(team, points):
    points = int(points)
    cityNum = int(teams[team]['lednum'])
    temp = teams[team]['color1']
    col1r = int(temp[1:3], 16)
    col1g = int(temp[3:5], 16)
    col1b = int(temp[5:7], 16)
    temp = teams[team]['color2']
    col2r = int(temp[1:3], 16)
    col2g = int(temp[3:5], 16)
    col2b = int(temp[5:7], 16)
    ba = bytearray()
    ba[0:8] = [cityNum, points, gamma[col1r], gamma[col1g], gamma[col1b], gamma[col2r], gamma[col2g], gamma[col2b], 0]
    for index, value in enumerate(ba):
        #ensures zerobyte is the sole zero.  Adjust values back on Arduino Side!
        ba[index] = min(255, value+1)
    ba[8] = int(0)
    ser.write(ba)


def lightup():
    pass


def cycle():
    myTeamNames = teams.keys()
    myTeamNames.sort()
    for key in myTeamNames:
        application(key, 4)
        time.sleep(6)


def league(whichLeague):
    socketFile = whichLeague + "Sockets.js"
    for path in execute(["node", socketFile]):
        matches = re.search("([\w\s\.]*)\+(\d{1,2}), (\d{1,3})", path)
        if matches is None:
            if path.startswith('close'):
                print("Closing down.")
                break
            print("Unknown line: {}".format(path))
            continue
        team = matches.group(1)
        delta = matches.group(2)
        total_points = matches.group(3)
        application(team, delta)
        print "{} {} {} {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                   team,
                                   delta,
                                   total_points,
                                   )


if __name__ == "__main__":
    funcToRun = sys.argv[1]
    if funcToRun in ["nba", "mlb", "nfl"]:
        league(funcToRun)
    elif funcToRun == "cycle":
        cycle()
