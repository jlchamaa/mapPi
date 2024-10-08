from abc import ABC, abstractmethod
import logging
import serial
from handlers.base import Handler
from teams import teams, gamma
log = logging.getLogger("mappy")
BLINK = True


class Score(Handler, ABC):
    def extra_init(self):
        self.scoreboard = {}
        self.blink = BLINK
        if self.blink:
            self.USB = serial.Serial('/dev/ttyACM0', 38400)

    @property
    @abstractmethod
    def league_name(self):
        raise NotImplementedError

    def is_relevant(self, obj):
        return (
            obj.get("topic", "").startswith(f"/{self.league_name}/gametracker")
            and obj.get("eventType") == "update"
        )

    def record_score(self, team, new_score):
        delta = new_score - self.scoreboard.get(team, 0)
        delta = min(10, max(0, delta))  # at least 0 no more than 10
        self.scoreboard[team] = new_score
        if delta > 0:
            msg = {"league": self.league_name, "team": team, "new_score": new_score, "delta": delta}
            log.info(msg)
            if self.blink:
                self.blink_score(team, delta)

    def blink_score(self, team, delta):
        league = self.league_name
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
        self.USB.write(ba)
