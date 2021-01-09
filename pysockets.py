#!/usr/bin/env python3.8
import asyncio
import json
import serial
import websockets
from teams import teams, gamma


ser = serial.Serial('/dev/ttyACM0', 38400)


class ScoreBoard:
    def __init__(self, league):
        self.scores = {}
        self.games = set()
        self.league = league

    def blink_map(self, team, delta):
        points = int(delta)
        cityNum = int(teams[team]['lednum'])
        temp = teams[team]['color1']
        col1r = int(temp[1:3], 16)
        col1g = int(temp[3:5], 16)
        col1b = int(temp[5:7], 16)
        temp = teams[team]['color2']
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

    def record_score(self, team, new_score):
        old_score = self.scores.get(team, 0)
        self.scores[team] = new_score
        delta = new_score - old_score
        if delta > 0 and delta < 10:
            print("{} scores {} -> {}".format(team, old_score, new_score))
            self.blink_map(team, new_score - old_score)


sb = ScoreBoard("nba")


def destring(obj):
    for _ in range(2):
        obj = json.loads(obj)
    return obj


def tostring(obj):
    for _ in range(2):
        obj = json.dumps(obj)
    return obj


async def subscribe_scoreboard(ws):
    req = {"cmd": "subscribe", "topics": ["/nba/scoreboard"]}
    await ws.send(tostring(req))


async def subscribe_to_game_topic(ws, game_topic):
    req = {"cmd": "subscribe", "topics": game_topic}
    await ws.send(tostring(req))


async def auth(ws):
    req = {"cmd": "login", "access_token": "64d1553ce024ab863adf69cff277b1f2ed75d961"}
    await ws.send(tostring(req))


async def handle(message, ws):
    if message == "o":
        print("auth time")
        await auth(ws)

    elif message == "h":
        return

    elif message[0] == "a":
        data = (destring(message[2:-1]))
        if data.get("authorized", None) == "ok":
            print("authorized. getting_scoreboard")
            await subscribe_scoreboard(ws)

        # top-line scoreboard update
        elif data.get("topic") == "/nba/scoreboard":
            if data.get("eventType") == "setState":
                for game_info in data["body"]["games"]:
                    game_id = game_info["abbr"]
                    game_topic = "/nba/gametracker/{}/ts".format(game_id)
                    if game_topic in sb.games:
                        continue
                    sb.games.add(game_topic)
                    print("subscribing to {}".format(game_topic))
                    await subscribe_to_game_topic(ws, game_topic)

        # per-game update
        elif data.get("topic") in sb.games:
            if data.get("body", False):  # non-subscriptions
                eventType = data["eventType"]
                if eventType == "setState":
                    print("setting state for {}".format(data.get("topic")))
                    for team in data["body"]["ts"]:
                        team_id = team["abbr"]
                        team_score = int(team["stats"]["points"])
                        sb.record_score(team_id, team_score)
                elif eventType == "update":
                    for team in data["body"]:
                        team_id = team["abbr"]
                        team_score = int(team["stats"]["points"])
                        sb.record_score(team_id, team_score)
        else:
            print(data)

    else:
        print(message)


async def try_nba():
    uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
    result = "open"
    async with websockets.connect(uri, ssl=True) as ws:
        while result != "close":
            try:
                message = await ws.recv()
                result = await handle(message, ws)
            except websockets.exceptions.ConnectionClosedError:
                return True
        return False


def main():
    el = asyncio.get_event_loop()
    trying = True
    while trying:
        trying = el.run_until_complete(try_nba())
        print("died for some reason")


if __name__ == "__main__":
    main()
