#!/usr/bin/env python3
import asyncio
import json
import logging
import random
from logging.handlers import TimedRotatingFileHandler
from teams import teams
from proxy import Proxy
from datetime import datetime
from zoneinfo import ZoneInfo
from textual.app import App
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import TextLog
TZ = ZoneInfo("America/Los_Angeles")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
)
h = TimedRotatingFileHandler("logs/out", when='midnight')
log = logging.getLogger()
log.addHandler(h)
log.info("Help")

class MApp(App):
    CSS_PATH = "my.css"
    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("e", "enable_log", "Enable the TextLog"),
    ]

    def compose(self):
        p = Proxy()
        self.do_logging = True
        yield p
        ls = []
        for league in ["nba", "nfl", "mlb"]:
            league_id = getattr(p.sb, league)
            s = ScoreUpdate(id=league)
            s.change_who(league_id)
            ls.append(s)
        s = ScoreUpdate(id="topics")
        s.change_who(p.sb.games)
        ls.append(s)
        yield Horizontal(
            ls[0],
            ls[1],
            ls[2],
            ls[3],
        )
        yield TextLog()

    def on_proxy_logmessage(self, event):
        if not self.do_logging:
            return
        curt = datetime.now(tz=TZ)
        if type(event.message) == str:
            m = f"{curt}  {event.message}"
        else:
            m = event.message
        log.info(m)
        self.get_log().write(m)

    def on_proxy_updatemessage(self, event):
        su = self.query_one(f"#{event.league}")
        if su.id == "topics":
            g = self.get_proxy().sb.games
            su.change_who(g)
        su.refresh()

    def get_proxy(self):
        return self.query_one(Proxy)

    def get_log(self):
        return self.query_one(TextLog)

    def action_quit_app(self):
        self.exit()

    def action_enable_log(self):
        # log = self.get_log()
        # with open("out.log", "w") as f:
        #     for line in log.lines:
        #         f.write(str(line))
        self.do_logging = not self.do_logging


class ScoreUpdate(Widget):
    who = reactive({}, layout=True)

    def render(self) -> str:
        if self.id == "topics":
            return str(list(self.who))
        return json.dumps([self.id, self.who], sort_keys=True, indent=2)

    def change_who(self, new_who):
        self.who = new_who


async def main():
    app = MApp()
    await app.run_async()
    # asyncio.create_task(try_map())
    # await start_table()


if __name__ == "__main__":
    # cycle()
    asyncio.run(main())
