from abc import ABC, abstractmethod
import json
import logging
# import serial
import traceback
from teams import teams, gamma
log = logging.getLogger("mappy")
# USB = serial.Serial('/dev/ttyACM0', 38400)


def tostring(obj):
    for _ in range(2):
        obj = json.dumps(obj)
    return obj


class Handler(ABC):
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
        except BaseException:
            if not (isinstance(obj, dict) or isinstance(obj, list)):
                obj = str(obj)
            traceback.print_exc()
            log.info(type(obj))
            log.info(str(obj))

    @abstractmethod
    def is_relevant(self, obj):
        raise NotImplementedError

    @abstractmethod
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
        self.log_q.put(req)
        await ws.send(tostring(req))


class League(Handler):
    def extra_init(self):
        self.topics = []

    @property
    @abstractmethod
    def league_name(self):
        raise NotImplementedError

    def is_relevant(self, obj):
        return (
            obj.get("topic") == f"/{self.league_name}/scoreboard"
            and obj.get("eventType") in ["update", "setState"]
        )

    async def handle(self, obj, ws):
        if obj.get("eventType") == "setState":
            await self.set_state(obj, ws)
        if obj.get("eventType") == "update":
            await self.update(obj, ws)

    async def set_state(self, obj, ws):
        games = obj.get("body", {}).get("games", [])
        for game in games:
            abbr = game.get("abbr")
            if abbr is None:
                self.log_q.put(obj)
                return
            if abbr not in self.topics:
                self.topics.append(abbr)
                gt_topic = f"/{self.league_name}/gametracker/{abbr}/ts"
                await self.subscribe_topic(ws, gt_topic)

    async def update(self, obj, ws):
        # await self.unsubscribe_topic(ws, f"/{self.league_name}/scoreboard")
        pass

    async def subscribe_topic(self, ws, topic):
        req = {"cmd": "subscribe", "topics": [topic]}
        self.log_q.put(req)
        await ws.send(tostring(req))

    async def unsubscribe_topic(self, ws, topic):
        req = {"cmd": "unsubscribe", "topics": [topic]}
        self.log_q.put(req)
        await ws.send(tostring(req))


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
