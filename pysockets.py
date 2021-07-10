#!/usr/bin/env python3.8
import asyncio
import json
import logging
import serial
import re
import time
import websockets
from teams import teams, gamma


logging.basicConfig(
    level="INFO",
    format='%(asctime)-15s %(message)s',
)
log = logging.getLogger("map")
ser = serial.Serial('/dev/ttyACM0', 38400)


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
        ba[0:8] = [cityNum, points, gamma[col1r], gamma[col1g], gamma[col1b], gamma[col2r], gamma[col2g], gamma[col2b], 0]
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
        if delta > 0 and delta < 10:
            self.blink_map(league, team, new_score - old_score)
            log.info("({}) {} scores {} -> {}".format(league, team, old_score, new_score))


sb = ScoreBoard()


def destring(obj):
    for _ in range(2):
        obj = json.loads(obj)
    return obj


def tostring(obj):
    for _ in range(2):
        obj = json.dumps(obj)
    return obj


async def subscribe_scoreboard(ws):
    req = {"cmd": "subscribe", "topics": ["/nba/scoreboard", "/nfl/scoreboard"]}
    await ws.send(tostring(req))


async def subscribe_to_game_topic(ws, game_topic):
    req = {"cmd": "subscribe", "topics": game_topic}
    await ws.send(tostring(req))


async def auth(ws):
    req = {"cmd": "login", "access_token": "64d1553ce024ab863adf69cff277b1f2ed75d961"}
    await ws.send(tostring(req))


def parse_nba_update(data):
    try:
        eventType = data["eventType"]
        if eventType == "setState":
            teams = data["body"]["ts"]
        elif eventType == "update":
            teams = data["body"]
        for team_data in teams:
            team_id = team_data["abbr"]
            team_score = int(team_data["stats"]["points"])
            sb.record_score("nba", team_id, team_score)
    except Exception as e:
        log.info(json.dumps(data, indent=2, sort_keys=True))
        log.warning("Problem in the NBA")
        log.info(e)


def parse_nfl_update(data):
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
        sb.record_score("nfl", teams[0], int(score_obj["away_score"]))
        sb.record_score("nfl", teams[1], int(score_obj["home_score"]))
    except Exception as e:
        log.info(json.dumps(data, indent=2, sort_keys=True))
        log.warning("Problem in the NFL")
        log.info(e)


def parse_update(data):
    league = data["topic"][1:4]
    if league == "nba":
        parse_nba_update(data)
    if league == "nfl":
        parse_nfl_update(data)


async def handle(message, ws):
    if message == "o":
        log.info("auth time")
        await auth(ws)

    elif message == "h":
        return

    elif message[0] == "a":
        data = (destring(message[2:-1]))
        if data.get("authorized", None) == "ok":
            log.info("authorized. getting_scoreboard")
            await subscribe_scoreboard(ws)

        # top-line scoreboard update
        elif "scoreboard" in data.get("topic") and data.get("eventType") == "setState":
            league = data["topic"][1:4]
            for game_info in data["body"]["games"]:
                game_id = game_info["abbr"]
                if league == "nfl":
                    game_topic = "/{}/gametracker/{}/scores".format(league, game_id)
                if league == "nba":
                    game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
                if game_topic in sb.games:
                    continue
                sb.games.add(game_topic)
                log.info("subscribing to {}".format(game_topic))
                await subscribe_to_game_topic(ws, game_topic)

        # per-game update
        elif data.get("topic") in sb.games and data.get("body", False):
            parse_update(data)

    else:
        log.info(message)


async def try_map():
    uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
    try:
        async with websockets.connect(uri, ssl=True) as ws:
            while True:
                message = await ws.recv()
                await handle(message, ws)
    except (websockets.exceptions.InvalidStatusCode, websockets.exceptions.ConnectionClosedError) as e:
        log.warning(e)



def main():
    while True:
        try:
            el = asyncio.get_event_loop()
            el.run_until_complete(try_map())
            log.warning("died for some reason")
            sb.clear_games()
            time.sleep(5)
        except Exception as e:
            log.warning("died for some very bad reason")
            log.warning(e)


def cycle():
    sb = ScoreBoard()
    while True:
        sb.blink_map("nba", "LAL", 3)
        time.sleep(5)

if __name__ == "__main__":
    # cycle()
    main()
