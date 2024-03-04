from datetime import datetime
from teams import teams, gamma
# import serial


class Scoreboard:
    def __init__(self):
        self.start = datetime.now().date()
        self.mlb = {}
        self.nba = {}
        self.nfl = {}
        self.games = set()
        # self.ser = serial.Serial('/dev/ttyACM0', 38400)

    def clear_games(self):
        current_day = datetime.now().date()
        if current_day != self.start:
            self.games = set()
            self.start = current_day

    def blink_map(self, league, team, delta):
        points = int(delta)
        cityNum = int(teams[league][team]['lednum'])
        temp = teams[league][team]['color1']
        col1r = int(temp[1:3], 16)
        col1g = int(temp[3:5], 16)
        col1b = int(temp[5:7], 16)
        temp = teams[league][team]['color2']
        col2r = int(temp[1:3], 16)
        col2g = int(temp[3:5], 16)
        col2b = int(temp[5:7], 16)
        ba = bytearray()
        ba[0:8] = [
            cityNum,
            points,
            gamma[col1r], gamma[col1g], gamma[col1b],
            gamma[col2r], gamma[col2g], gamma[col2b],
            0,  # trailing zero needed for Arduino
        ]
        for index, value in enumerate(ba):
            # ensures zerobyte is the sole zero.  Adjust values back on Arduino Side!
            ba[index] = min(255, value + 1)
        ba[8] = int(0)
        # self.ser.write(ba)

    def record_score(self, league, team, new_score):
        scores = getattr(self, league)
        old_score = scores.get(team, 0)
        scores[team] = new_score
        delta = new_score - old_score
        if delta > 0 and delta < 15:
            self.blink_map(league, team, new_score - old_score)
        return "({}) {} scores {} -> {}".format(league, team, old_score, new_score)
