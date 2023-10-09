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
        log.info("We're READY")
        req = {
            "cmd": "subscribe",
            "topics": [
                # "/mlb/scoreboard",
                "/nfl/scoreboard",
                # "/nba/scoreboard",
        ]}
        TOPICS.extend(req["topics"])
        await ws.send(tostring(req))



async def subscribe_scoreboard(ws):
    req = {"cmd": "subscribe", "topics": ["/mlb/scoreboard", "/nfl/scoreboard", "/nba/scoreboard"]}
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


async def auth(ws):
    req = {"cmd": "login", "access_token": "64d1553ce024ab863adf69cff277b1f2ed75d961"}
    await ws.send(tostring(req))

def destring(obj):
    for _ in range(2):
        obj = json.loads(obj)
    return obj

async def handle_by_topic(self, data, ws):
    topic = data.get("topic", "")
    if topic == "":
        log.warn("No topic for this data")
        log.warn(data)
    elif topic.startswith("/nba/"):
        log.debug("nba")
        await self.handle_nba(data, ws)
    elif topic.startswith("/nfl/"):
        log.debug("nfl")
        await self.handle_nfl(data, ws)
    elif topic.startswith("/mlb/"):
        log.debug("mlb")
        await self.handle_mlb(data, ws)
    else:
        self.logwrite(data)

    async def handle(self, message, ws):
        log.info("Handling something")
        if message == "o":
            self.logwrite("auth time")
            await auth(ws)
        elif message[0] == "a":
            data = (destring(message[2:-1]))
            if data.get("authorized", None) == "ok":
                log.info("authorized. getting_scoreboard")
                await subscribe_scoreboard(ws)
            else:
                await self.handle_by_topic(data, ws)
        else:
            self.logwrite(message)

