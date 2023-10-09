#!/usr/bin/env python3
import asyncio
import json
import logging
import websockets
import traceback
from logging.handlers import TimedRotatingFileHandler
from handlers.scoreboard import Scoreboard
from handlers import all_handlers
h = TimedRotatingFileHandler("logs/out", when='H')
h.setFormatter(logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
))
log = logging.getLogger("mappy")
log.setLevel(logging.DEBUG)
log.addHandler(h)
log.info("Help")


def run(score_q, log_q):
    my_map = Map(score_q, log_q)
    asyncio.run(my_map.try_map())


def destring(obj):
    obj = obj[2:-1]
    obj = json.loads(obj)
    obj = json.loads(obj)
    return obj


def tostring(obj):
    for _ in range(2):
        obj = json.dumps(obj)
    return obj


class Map():
    def __init__(self, score_q, log_q):
        self.score_q = score_q
        self.log_q = log_q
        self.sb = Scoreboard()
        self.handlers = self.build_handler(
            self.score_q,
            self.log_q,
        )

    def build_handler(self, sc, lo):
        return [h(sc, lo) for h in all_handlers]

    @staticmethod
    def transform(msg):
        if len(msg) < 4:
            if msg == "o":
                return {"auth": "ready"}
            else:
                log.error("Weird short message")
                log.error(msg)
        try:
            return destring(msg)
        except:
            log.error("Un-de-stringable massage")
            log.error(msg)
            raise

    async def attempt_all(self, msg, ws):
        obj = self.transform(msg)
        for h in self.handlers:
            await h.attempt(obj, ws)

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
