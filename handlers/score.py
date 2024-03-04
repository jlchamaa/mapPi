import logging
# import serial
from handlers.base import Handler
from teams import teams, gamma
log = logging.getLogger("mappy")
# USB = serial.Serial('/dev/ttyACM0', 38400)


class Score(Handler):
    def extra_init(self):
        self.scoreboard = {}

    def record_score(self, league, team, new_score):
        delta = new_score - self.scoreboard.get(team, 0)
        delta = min(10, max(0, delta))  # at least 0 no more than 10
        self.scoreboard[team] = new_score
        if delta > 0:
            msg = {"league": league, "team": team, "new_score": new_score, "delta": delta}
            self.log_q.put(msg)
            log.info(msg)
            self.blink_score(league, team, delta)
        self.score_q.put({league: {team: new_score}, "topics": ["lol"]})

    def blink_score(self, league, team, delta):
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
        # USB.write(ba)
