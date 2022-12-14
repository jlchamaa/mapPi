#!/usr/bin/env python3
import asyncio
import json
import logging
# import serial
import traceback
import random
import re
import websockets
from teams import teams, gamma

from textual.app import App
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, TextLog


logging.basicConfig(
    level="INFO",
    format='%(asctime)-15s %(message)s',
    # filename="map.log",
)
log = logging.getLogger("map")
log.write = lambda x: log.info(x)
# ser = serial.Serial('/dev/ttyACM0', 38400)


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


class MApp(App):
    CSS_PATH = "my.css"
    BINDINGS = [
        ("s", "trigger_score", "Trigger random scoring event"),
        ("q", "quit_app", "Quit"),
        ("e", "enable_log", "Enable the TextLog"),
    ]

    def compose(self):
        p = Proxy()
        yield p
        ls = []
        for league in [p.sb.nba, p.sb.nfl, p.sb.mlb]:
            s = ScoreUpdate()
            s.change_who(league)
            ls.append(s)
        yield Horizontal(
            ls[0],
            ls[1],
            ls[2],
        )
        yield MyTextLog()

    def get_proxy(self):
        return self.query_one(Proxy)

    def get_log(self):
        return self.query_one(TextLog)

    def action_quit_app(self):
        self.exit()

    def action_enable_log(self):
        self.get_log().write("Try this!")

    def action_trigger_score(self) -> None:
        try:
            i = random.randint(0, 2)
            rand_league = list(teams.keys())[i]
            league_teams = list(teams[rand_league].keys())
            i = random.randrange(len(league_teams))
            rand_team = league_teams[i]
            scoring = random.randint(1, 3)
            sb = self.get_proxy().sb
            new_score = getattr(sb, rand_league).get(rand_team, 0) + scoring
            sb.record_score(rand_league, rand_team, new_score)
            self.get_log().write(f"{rand_league}: {rand_team} +{scoring} {new_score}")
            self.refresh()

        except Exception as e:
            self.get_log().write(e)

    def watch_reacter(self, older, newer):
        pass


class MyTextLog(TextLog):
    def on_mount(self) -> None:
        self.styles.height = 20


class ScoreUpdate(Widget):
    who = reactive({}, layout=True)

    def render(self) -> str:
        return json.dumps(self.who, sort_keys=True, indent=2)

    def change_who(self, new_who):
        self.who = new_who


class Proxy(Static):
    sb = reactive(ScoreBoard())

    class Topical(Message):
        pass


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


def parse_nba_update(data):
    log.write("NBA Update")
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
        traceback.print_exc()
        log.write(json.dumps(data, indent=2, sort_keys=True))
        log.write("Problem in the NBA")
        log.write(e)


def parse_nfl_update(data):
    log.write("NFL Update")
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
        log.write(json.dumps(data, indent=2, sort_keys=True))
        log.write("Problem in the NFL")
        log.write(e)


def parse_mlb_update(data):
    log.write("MLB Update")
    try:
        et = data["eventType"]
        if et != "update":
            return
        for entry in data["body"]:
            team_id = entry["abbr"]
            score = int(entry["batting"]["runs"])
            sb.record_score("mlb", team_id, score)
    except Exception as e:
        log.write("Problem in the MLB")
        log.write(e)
        log.write(json.dumps(data, indent=2))


def parse_update(data):
    league = data["topic"][1:4]
    if league == "nba":
        parse_nba_update(data)
    elif league == "nfl":
        parse_nfl_update(data)
    elif league == "mlb":
        parse_mlb_update(data)
    else:
        log.write(f"Can't pase update with topic {data['topic']}")


async def handle(message, ws):
    if message == "o":
        log.write("auth time")
        await auth(ws)

    elif message == "h":
        return

    elif message[0] == "a":
        data = (destring(message[2:-1]))
        topic = data.get("topic")
        if data.get("authorized", None) == "ok":
            log.write("authorized. getting_scoreboard")
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
                if game_topic in sb.games:
                    continue
                sb.games.add(game_topic)
                log.write("subscribing to {}".format(game_topic))
                await subscribe_to_game_topic(ws, game_topic)

        # per-game update
        elif topic in sb.games and data.get("body", False):
            parse_update(data)
        else:
            log.write("unimportant message")

    else:
        log.write(message)


async def try_map():
    uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
    try:
        async with websockets.connect(uri, ssl=True) as ws:
            while True:
                message = await ws.recv()
                await handle(message, ws)
    except (websockets.exceptions.InvalidStatusCode, websockets.exceptions.ConnectionClosedError) as e:
        log.write("Death was a websocket issue")
        log.write(e)


async def main():
    app = MApp()
    await app.run_async()
    # asyncio.create_task(try_map())
    # await start_table()


if __name__ == "__main__":
    # cycle()
    asyncio.run(main())
