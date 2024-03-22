#!/usr/bin/env python3
from multiprocessing import Queue
from datetime import datetime
import asyncio
import json
import logging
import websockets
from handlers import all_handlers
CBS_URI = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger("mappy")
log.setLevel(logging.INFO)


def run(score_q, log_q):
    my_map = Map(score_q, log_q)
    result = asyncio.run(my_map.try_map())
    log.info(f"We recieved this result: {result}!")


def destring(obj):
    obj = obj[2:-1]
    obj = json.loads(obj)
    obj = json.loads(obj)
    return obj


class Map():
    def __init__(self, score_q, log_q):
        self.score_q = score_q
        self.log_q = log_q
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
        except BaseException:
            log.error("Un-de-stringable massage")
            log.error(msg)
            raise

    async def attempt_all(self, msg, ws):
        obj = self.transform(msg)
        for h in self.handlers:
            await h.attempt(obj, ws)

    async def try_map(self):
        start_day = datetime.now().strftime("%x")
        log.info(f"Trying map on date {start_day}")
        try:
            async with websockets.connect(CBS_URI, ssl=True) as ws:
                while True:
                    message = await ws.recv()
                    await self.attempt_all(message, ws)
                    if datetime.now().strftime("%x") != start_day:
                        # a new day has sprung!
                        return 0
            return 4
        except (websockets.exceptions.ConnectionClosedOK) as e:
            log.info("Closed for normal reasons")
            log.info(e)
            return 1

        except (
                websockets.exceptions.InvalidStatusCode,
                websockets.exceptions.ConnectionClosedError,
        ) as e:
            log.info("Closed for BAD reasons")
            log.info(e)
            return 2
        except (KeyboardInterrupt, BaseException) as e:
            log.info("Closed for other exception")
            log.info(e)
            return 3


if __name__ == "__main__":
    run(Queue(), Queue())
