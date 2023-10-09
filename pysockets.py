#!/usr/bin/env python3
import asyncio
import json
import logging
import websockets
import traceback
from logging.handlers import TimedRotatingFileHandler
from handlers.scoreboard import Scoreboard
from handlers import (
    AuthHandler,
    BaseHandler,
    NBAHandler,
    NFLHandler,
    MLBHandler,
)
h = TimedRotatingFileHandler("logs/out", when='H')
h.setFormatter(logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
))
log = logging.getLogger("mappy")
log.setLevel(logging.DEBUG)
log.addHandler(h)
log.info("Help")


def run():
    my_map = Map()
    asyncio.run(my_map.try_map())


class Map():
    def __init__(self):
        self.sb = Scoreboard()
        self.handlers = self.build_handler()

    def build_handler(self):
        return [BaseHandler(), AuthHandler()]

    async def attempt_all(self, msg, ws):
        for h in self.handlers:
            await h.attempt(msg, ws)

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


    def record_score():
        pass

    async def try_map(self):
        log.info("Trying map")
        uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
        try:
            async with websockets.connect(uri, ssl=True) as ws:
                while True:
                    message = await ws.recv()
                    await self.attempt_all(message, ws)
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

if __name__ == "__main__":
    run()
