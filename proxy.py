#!/usr/bin/env python3
import asyncio
import json
# import serial
import traceback
import re
import websockets
from teams import teams, gamma

from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static
# ser = serial.Serial('/dev/ttyACM0', 38400)


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
    await ws.send(tostring(req))


async def subscribe_to_game_topic(ws, game_topic):
    req = {"cmd": "subscribe", "topics": [game_topic]}
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
        # ser.write(ba)

    def record_score(self, league, team, new_score):
        scores = getattr(self, league)
        old_score = scores.get(team, 0)
        scores[team] = new_score
        delta = new_score - old_score
        if delta > 0 and delta < 10:
            self.blink_map(league, team, new_score - old_score)
            # log.write("({}) {} scores {} -> {}".format(league, team, old_score, new_score))


class Proxy(Static):
    sb = reactive(ScoreBoard())

    class Logmessage(Message):
        def __init__(self, sender, message):
            self.message = message
            super().__init__(sender)

    async def logwrite(self, line):
        self.styles.background = "green"
        await self.emit(self.Logmessage(self, line))

    def on_mount(self):
        asyncio.create_task(self.try_map())

    async def parse_nba_update(self, data):
        await self.logwrite("NBA Update")
        try:
            eventType = data["eventType"]
            if eventType == "setState":
                teams = data["body"]["ts"]
            elif eventType == "update":
                teams = data["body"]
            for team_data in teams:
                team_id = team_data["abbr"]
                team_score = int(team_data["stats"]["points"])
                self.sb.record_score("nba", team_id, team_score)
        except Exception as e:
            traceback.print_exc()
            await self.logwrite(json.dumps(data, indent=2, sort_keys=True))
            await self.logwrite("Problem in the NBA")
            await self.logwrite(e)

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
            self.sb.record_score("nfl", teams[0], int(score_obj["away_score"]))
            self.sb.record_score("nfl", teams[1], int(score_obj["home_score"]))
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
                self.sb.record_score("mlb", team_id, score)
        except Exception as e:
            await self.logwrite("Problem in the MLB")
            await self.logwrite(e)
            await self.logwrite(json.dumps(data, indent=2))

    async def parse_update(self, data):
        league = data["topic"][1:4]
        if league == "nba":
            await self.parse_nba_update(data)
        elif league == "nfl":
            await self.parse_nfl_update(data)
        elif league == "mlb":
            await self.parse_mlb_update(data)
        else:
            await self.logwrite(f"Can't pase update with topic {data['topic']}")

    async def handle(self, message, ws):
        if message == "o":
            await self.logwrite("auth time")
            await auth(ws)

        elif message == "h":
            return

        elif message[0] == "a":
            data = (destring(message[2:-1]))
            topic = data.get("topic")
            if data.get("authorized", None) == "ok":
                await self.logwrite("authorized. getting_scoreboard")
                await subscribe_scoreboard(ws)

            # top-line scoreboard update
            elif "scoreboard" in topic and data.get("eventType") == "setState":
                league = topic[1:4]
                for game_info in data["body"]["games"]:
                    game_id = game_info["abbr"]
                    if league == "nfl":
                        game_topic = "/{}/gametracker/{}/scores".format(league, game_id)
                    if league == "nba":
                        game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
                    if league == "mlb":
                        game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
                    if game_topic in self.sb.games:
                        continue
                    self.sb.games.add(game_topic)
                    await self.logwrite("subscribing to {}".format(game_topic))
                    await subscribe_to_game_topic(ws, game_topic)

            # per-game update
            elif topic in self.sb.games and data.get("body", False):
                await self.parse_update(data)
            else:
                await self.logwrite("unimportant message")

        else:
            await self.logwrite(message)

    async def try_map(self):
        uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
        try:
            async with websockets.connect(uri, ssl=True) as ws:
                while True:
                    message = await ws.recv()
                    await self.handle(message, ws)
        except (websockets.exceptions.InvalidStatusCode, websockets.exceptions.ConnectionClosedError) as e:
            await self.logwrite("Death was a websocket issue")
            await self.logwrite(e)
