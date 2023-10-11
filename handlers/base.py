import abc
import json
import logging
import serial
import traceback
from teams import teams, gamma
log = logging.getLogger("mappy")
USB = serial.Serial('/dev/ttyACM0', 38400)

def tostring(obj):
    for _ in range(2):
        obj = json.dumps(obj)
    return obj


class Handler(abc.ABC):
    def __init__(self, score_q, log_q):
        self.score_q = score_q
        self.log_q = log_q
        self.extra_init()

    def extra_init(self):
        pass

    async def attempt(self, obj, ws):
        try:
            if self.is_relevant(obj):
                await self.handle(obj, ws)
        except BaseException as e:
            if not (isinstance(obj, dict) or isinstance(obj, list)):
                obj = str(obj)
            traceback.print_exc()
            log.info(type(obj))
            log.info(str(obj))


    @abc.abstractmethod
    def is_relevant(self, obj):
        raise NotImplementedError

    @abc.abstractmethod
    async def handle(self, obj, ws):
        raise NotImplementedError


class Base(Handler):
    def is_relevant(self, obj):
        return False

    async def handle(self, obj, ws):
        self.log_q.put(obj)


class Auth(Handler):
    def is_relevant(self, obj):
        return obj.get("auth") == "ready"

    async def handle(self, message, ws):
        req = {
            "cmd": "login",
            "access_token": "64d1553ce024ab863adf69cff277b1f2ed75d961",
        }
        await ws.send(tostring(req))


class ScoreboardSubscription(Handler):
    def is_relevant(self, obj):
        return obj.get("authorized") == "ok"

    async def handle(self, message, ws):
        req = {
            "cmd": "subscribe",
            "topics": [
                "/mlb/scoreboard",
                "/nfl/scoreboard",
                "/nba/scoreboard",
        ]}
        await ws.send(tostring(req))

class League(Handler):
    def extra_init(self):
        self.topics = []

    async def subscribe_topic(self, ws, topic):
        req = {"cmd": "subscribe", "topics": [topic]}
        await ws.send(tostring(req))


    async def unsubscribe_topic(self, ws, topic):
        req = {"cmd": "unsubscribe", "topics": [topic]}
        await ws.send(tostring(req))


class Score(Handler):
    def extra_init(self):
        self.scoreboard = {}

    def record_score(self, league, team, new_score):
        delta = new_score - self.scoreboard.get(team, 0)
        delta = min(10, max(0, delta))  # at least 0 no more than 10
        self.scoreboard[team] = new_score
        self.blink_score(league, team, delta)

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
        USB.write(ba)
