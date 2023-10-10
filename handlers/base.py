import abc
import json
import logging
log = logging.getLogger("mappy")
TOPICS = []


def tostring(obj):
    for _ in range(2):
        obj = json.dumps(obj)
    return obj


class Handler(abc.ABC):
    def __init__(self, score_q, log_q):
        self.score_q = score_q
        self.log_q = log_q

    async def attempt(self, obj, ws):
        if self.is_relevant(obj):
            await self.handle(obj, ws)


    @abc.abstractmethod
    def is_relevant(self, obj):
        raise NotImplementedError

    @abc.abstractmethod
    async def handle(self, obj, ws):
        raise NotImplementedError


class Base(Handler):
    def is_relevant(self, obj):
        return True

    async def handle(self, obj, ws):
        log.info(f"msg of length {len(str(obj))}")
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
        TOPICS.extend(req["topics"])
        await ws.send(tostring(req))



async def unsubscribe_topic(ws, topic):
    req = {"cmd": "unsubscribe", "topics": [topic]}
    if topic in TOPICS:
        TOPICS.remove(topic)
    await ws.send(tostring(req))


async def subscribe_to_game_topic(ws, game_topic):
    req = {"cmd": "subscribe", "topics": [game_topic]}
    TOPICS.append(game_topic)
    await ws.send(tostring(req))
