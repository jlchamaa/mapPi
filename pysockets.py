#!/usr/bin/env python3
import asyncio
import json
import random
from teams import teams
from proxy import Proxy

from textual.app import App
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import TextLog


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
        for league in ["nba", "nfl", "mlb"]:
            league_d = getattr(p.sb, league)
            s = ScoreUpdate(id=league)
            s.change_who(league_d)
            ls.append(s)
        yield Horizontal(
            ls[0],
            ls[1],
            ls[2],
        )
        yield MyTextLog()

    def on_proxy_logmessage(self, event):
        self.get_log().write(event.message)

    def on_proxy_updatemessage(self, event):
        self.query_one(f"#{event.league}").refresh()

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
            widg = self.query_one(f"#{rand_league}")
            widg.refresh()

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
