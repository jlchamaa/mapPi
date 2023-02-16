#!/usr/bin/env python3
import asyncio
import json
import logging
import serial
import traceback
import re
import websockets
from teams import teams, gamma

from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static
log = logging.getLogger()
ser = serial.Serial('/dev/ttyACM0', 38400)
TOPICS = []


def destring(obj):
    for _ in range(2):
        obj = json.loads(obj)
    return obj


def tostring(obj):
    for _ in range(2):
        obj = json.dumps(obj)
    return obj


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


class ScoreBoard:
    def __init__(self):
        self.mlb = {}
        self.nba = {}
        self.nfl = {}
        self.games = set()

    def clear_games(self):
        self.games = set()

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
        ser.write(ba)

    def record_score(self, league, team, new_score):
        scores = getattr(self, league)
        old_score = scores.get(team, 0)
        scores[team] = new_score
        delta = new_score - old_score
        if delta > 0 and delta < 15:
            self.blink_map(league, team, new_score - old_score)
        return "({}) {} scores {} -> {}".format(league, team, old_score, new_score)


class Proxy(Static):
    sb = reactive(ScoreBoard())
    topics = reactive(TOPICS)

    class Updatemessage(Message):
        def __init__(self, sender, league):
            self.league = league
            super().__init__(sender)

    class Logmessage(Message):
        def __init__(self, sender, message):
            self.message = message
            super().__init__(sender)

    def render(self):
        return "Proxy"

    async def logwrite(self, line):
        await self.emit(self.Logmessage(self, line))

    def on_mount(self):
        asyncio.create_task(self.map_loop())

    async def map_loop(self):
        # while True:
        self.sb.clear_games()
        # TODO only clear if the date doesn't match today
        try_again = await self.try_map()
        await self.logwrite(f"Try Map finished and returned {try_again}")


    async def parse_nfl_update(self, data):
        await self.logwrite("NFL Update")
        try:
            teams = re.search(r"_(\w{2,3})@(\w{2,3})", data["topic"]).groups()
            if "scores" in data["body"]:
                score_list = data["body"]["scores"]
                if len(score_list) > 0:
                    score_obj = score_list[-1]
                else:
                    return
            else:
                score_obj = data["body"][0]
            r = self.sb.record_score("nfl", teams[0], int(score_obj["away_score"]))
            await self.logwrite(r)
            r = self.sb.record_score("nfl", teams[1], int(score_obj["home_score"]))
            await self.logwrite(r)
            await self.emit(self.Updatemessage(self, "nfl"))
        except Exception as e:
            await self.logwrite(json.dumps(data, indent=2, sort_keys=True))
            await self.logwrite("Problem in the NFL")
            await self.logwrite(e)

    async def parse_mlb_update(self, data):
        await self.logwrite("MLB Update")
        try:
            et = data["eventType"]
            if et != "update":
                return
            for entry in data["body"]:
                team_id = entry["abbr"]
                score = int(entry["batting"]["runs"])
                r = self.sb.record_score("mlb", team_id, score)
                await self.logwrite(r)
                await self.emit(self.Updatemessage(self, "mlb"))
        except Exception as e:
            await self.logwrite("Problem in the MLB")
            await self.logwrite(e)
            await self.logwrite(json.dumps(data, indent=2))

    async def handle_nba(self, data, ws):
        topic = data.get("topic", "")
        event_type = data.get("eventType", "")
        await self.logwrite(f"Nba: {topic}: {event_type}")
        if "scoreboard" in topic:
            # populate scoreboard
            if event_type == "setState":
                await self.logwrite("nba 1")
                league = topic[1:4]
                if "body" not in data:
                    await self.logwrite(f"bodyless data for {topic}")
                    await self.logwrite(data)
                    return
                for game_info in data["body"]["games"]:
                    if "abbr" not in game_info:
                        await self.logwrite("We didn't have an abbr??")
                        await self.logwrite(topic)
                        continue
                    game_id = game_info["abbr"]
                    game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
                    if game_topic in self.sb.games:
                        await self.emit(self.Updatemessage(self, "topics"))
                        continue
                    self.sb.games.add(game_topic)
                    await self.logwrite("subscribing to {}".format(game_topic))
                    await subscribe_to_game_topic(ws, game_topic)
            else:
                # we got the scoreboard, so get out
                await self.logwrite("nba 2")
                await unsubscribe_topic(ws, topic)
                await self.logwrite(f"Unsubscribed {topic}")
        elif "gametracker" in topic:
            await self.logwrite("nba 3")
            try:
                if event_type == "":
                    await self.logwrite("nba 5")
                    return
                if event_type == "setState":
                    teams = data["body"]["ts"]
                elif event_type == "update":
                    teams = data["body"]
                for team_data in teams:
                    team_id = team_data["abbr"]
                    team_score = int(team_data["stats"]["points"])
                    r = self.sb.record_score("nba", team_id, team_score)
                    await self.logwrite(r)
                    await self.emit(self.Updatemessage(self, "nba"))
            except Exception as e:
                await self.logwrite("Problem in the NBA")
                await self.logwrite(traceback.format_exc())
                await self.logwrite(json.dumps(data, indent=2, sort_keys=True))
                await self.logwrite(e)
        else:
            await self.logwrite("nba 4")
            await self.logwrite(data)

    async def handle_nfl(self, data, ws):
        # elif "scoreboard" in topic and data.get("eventType") != "setState":
        #     if "nfl" not in topic:
        #         await unsubscribe_topic(ws, topic)
        #         await self.logwrite(f"Unsubscribed {topic}")
        # elif "scoreboard" in topic:
        #     league = topic[1:4]
        #     if "body" not in data:
        #         await self.logwrite(f"bodyless data for {topic}")
        #         await self.logwrite(data)
        #         return
        #     for game_info in data["body"]["games"]:
        #         if "abbr" not in game_info:
        #             await self.logwrite(f"We didn't have an abbr??")
        #             await self.logwrite(topic)
        #             continue
        #         game_id = game_info["abbr"]
        #         if league == "nfl":
        #             game_topic = "/{}/gametracker/{}/scores".format(league, game_id)
        #         if league == "nba":
        #             game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
        #         if league == "mlb":
        #             game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
        #         if game_topic in self.sb.games:
        #             await self.emit(self.Updatemessage(self, "topics"))
        #             continue
        #         self.sb.games.add(game_topic)
        #         await self.logwrite("subscribing to {}".format(game_topic))
        #         await subscribe_to_game_topic(ws, game_topic)
        # per-game update
        pass

    async def handle_mlb(self, data, ws):
        # elif "scoreboard" in topic and data.get("eventType") != "setState":
        #     if "nfl" not in topic:
        #         await unsubscribe_topic(ws, topic)
        #         await self.logwrite(f"Unsubscribed {topic}")
        # elif "scoreboard" in topic:
        #     league = topic[1:4]
        #     if "body" not in data:
        #         await self.logwrite(f"bodyless data for {topic}")
        #         await self.logwrite(data)
        #         return
        #     for game_info in data["body"]["games"]:
        #         if "abbr" not in game_info:
        #             await self.logwrite(f"We didn't have an abbr??")
        #             await self.logwrite(topic)
        #             continue
        #         game_id = game_info["abbr"]
        #         if league == "nfl":
        #             game_topic = "/{}/gametracker/{}/scores".format(league, game_id)
        #         if league == "nba":
        #             game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
        #         if league == "mlb":
        #             game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
        #         if game_topic in self.sb.games:
        #             await self.emit(self.Updatemessage(self, "topics"))
        #             continue
        #         self.sb.games.add(game_topic)
        #         await self.logwrite("subscribing to {}".format(game_topic))
        #         await subscribe_to_game_topic(ws, game_topic)
        # per-game update
        pass

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
            await self.handle_nfl(data, ws)
        else:
            await self.logwrite(data)

    async def handle(self, message, ws):
        if message == "o":
            await self.logwrite("auth time")
            await auth(ws)
        elif message[0] == "a":
            data = (destring(message[2:-1]))
            if data.get("authorized", None) == "ok":
                log.info("authorized. getting_scoreboard")
                await subscribe_scoreboard(ws)
            else:
                await self.handle_by_topic(data, ws)
        else:
            await self.logwrite(message)

    async def try_map(self):
        uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
        try:
            async with websockets.connect(uri, ssl=True) as ws:
                while True:
                    message = await ws.recv()
                    await self.handle(message, ws)
        except (websockets.exceptions.ConnectionClosedOK) as e:
            await self.logwrite("Closed for normal reasons")
            await self.logwrite(e)
            return 0

        except (websockets.exceptions.InvalidStatusCode, websockets.exceptions.ConnectionClosedError) as e:
            await self.logwrite("Closed for BAD reasons")
            await self.logwrite(e)
            return 1
        except BaseException as e:
            await self.logwrite("Closed for other exception")
            await self.logwrite(e)
            await self.logwrite(traceback.format_exc())
            return 1
