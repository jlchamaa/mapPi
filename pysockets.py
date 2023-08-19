#!/usr/bin/env python3
import asyncio
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from proxy import Proxy, TOPICS
from datetime import datetime, timezone, timedelta
import threading
TZ = timezone(timedelta(hours=-8.0))
h = TimedRotatingFileHandler("logs/out", when='H')
h.setFormatter(logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
))
log = logging.getLogger("mappy")
log.setLevel(logging.DEBUG)
log.addHandler(h)
log.info("Help")
log.info(log.handlers)


# def make_scoreboard():
#     p = Proxy()
#     for league in ["nba", "nfl", "mlb"]:
#     league_id = getattr(p.sb, league)
#     s = ScoreUpdate(id=league)
#     s.change_who(league_id)
#     ls.append(s)
#     s = ScoreUpdate(id="topics")
#     s.change_who(p.topics)
#     ls.append(s)


def run():
    proxy = Proxy()
    asyncio.run(proxy.try_map())


if __name__ == "__main__":
    run()
    # cycle()
