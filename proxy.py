#!/usr/bin/env python3
import asyncio
from datetime import datetime
import json
import logging
import serial
import traceback
import re
import websockets
from teams import teams, gamma

log = logging.getLogger("mappy")
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
        self.start = datetime.now().date()
        self.mlb = {}
        self.nba = {}
        self.nfl = {}
        self.games = set()

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
        ser.write(ba)

    def record_score(self, league, team, new_score):
        scores = getattr(self, league)
        old_score = scores.get(team, 0)
        scores[team] = new_score
        delta = new_score - old_score
        if delta > 0 and delta < 15:
            self.blink_map(league, team, new_score - old_score)
        return "({}) {} scores {} -> {}".format(league, team, old_score, new_score)


class Proxy():
    def __init__(self):
        self.sb = ScoreBoard()
        self.topics = TOPICS

    def logwrite(self, line, data=False):
        if not data:
            log.info(line)
            # await self.emit(self.Logmessage(self, line))
        else:
            log.info(line)

    def map_loop(self):
        try_again = True
        while try_again:
            self.logwrite(f"Trying Map Loop")
            self.sb.clear_games()
            try_again = self.try_map()
            self.logwrite(f"Try Map finished and returned {try_again}")


    async def handle_nba(self, data, ws):
        topic = data.get("topic", "")
        event_type = data.get("eventType", "")
        if "scoreboard" in topic:
            # populate scoreboard
            if event_type == "setState":
                league = topic[1:4]
                if "body" not in data:
                    self.logwrite(f"bodyless data for {topic}")
                    self.logwrite(data)
                    return
                for game_info in data["body"]["games"]:
                    if "abbr" not in game_info:
                        self.logwrite("We didn't have an abbr??")
                        self.logwrite(topic)
                        continue
                    game_id = game_info["abbr"]
                    game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
                    if game_topic in self.sb.games:
                        # await self.emit(self.Updatemessage(self, "topics"))
                        continue
                    self.sb.games.add(game_topic)
                    self.logwrite("subscribing to {}".format(game_topic))
                    await subscribe_to_game_topic(ws, game_topic)
            else:
                # we got the scoreboard, so get out
                await unsubscribe_topic(ws, topic)
                self.logwrite(f"Unsubscribed {topic}")
        elif "gametracker" in topic:
            try:
                if event_type == "":
                    return
                if event_type == "setState":
                    teams = data["body"]["ts"]
                elif event_type == "update":
                    teams = data["body"]
                else:
                    self.logwrite(event_type)
                    return
                for team_data in teams:
                    team_id = team_data["abbr"]
                    team_score = int(team_data["stats"]["points"])
                    r = self.sb.record_score("nba", team_id, team_score)
                    self.logwrite(r)
                    # await self.emit(self.Updatemessage(self, "nba"))
            except Exception as e:
                self.logwrite("Problem in the NBA")
                self.logwrite(traceback.format_exc())
                self.logwrite(json.dumps(data, indent=2, sort_keys=True))
                self.logwrite(e)
        else:
            self.logwrite("nba 4")
            self.logwrite(data)

    async def handle_nfl(self, data, ws):
        return
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
            self.logwrite(r)
            r = self.sb.record_score("nfl", teams[1], int(score_obj["home_score"]))
            self.logwrite(r)
            # await self.emit(self.Updatemessage(self, "nfl"))
        except Exception as e:
            self.logwrite(json.dumps(data, indent=2, sort_keys=True))
            self.logwrite("Problem in the NFL")
            self.logwrite(e)

    async def handle_mlb(self, data, ws):
        return
        try:
            et = data["eventType"]
            if et != "update":
                return
            for entry in data["body"]:
                team_id = entry["abbr"]
                score = int(entry["batting"]["runs"])
                r = self.sb.record_score("mlb", team_id, score)
                await self.logwrite(r)
                # await self.emit(self.Updatemessage(self, "mlb"))
        except Exception as e:
            self.logwrite("Problem in the MLB")
            self.logwrite(e)
            self.logwrite(json.dumps(data, indent=2))

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
        log.info(message)
        return
        # if message == "o":
        #     self.logwrite("auth time")
        #     await auth(ws)
        # elif message[0] == "a":
        #     data = (destring(message[2:-1]))
        #     if data.get("authorized", None) == "ok":
        #         log.info("authorized. getting_scoreboard")
        #         await subscribe_scoreboard(ws)
        #     else:
        #         await self.handle_by_topic(data, ws)
        # else:
        #     self.logwrite(message)

    async def try_map(self):
        log.info("Trying map")
        uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
        try:
            async with websockets.connect(uri, ssl=True) as ws:
                while True:
                    message = await ws.recv()
                    await self.handle(message, ws)
        except (websockets.exceptions.ConnectionClosedOK) as e:
            self.logwrite("Closed for normal reasons")
            self.logwrite(e)
            return True

        except (websockets.exceptions.InvalidStatusCode, websockets.exceptions.ConnectionClosedError) as e:
            self.logwrite("Closed for BAD reasons")
            self.logwrite(e)
            return False
        except (KeyboardInterrupt, BaseException) as e:
            self.logwrite("Closed for other exception")
            self.logwrite(e)
            self.logwrite(traceback.format_exc())
            return False
