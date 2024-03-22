#!/usr/bin/env python3
from multiprocessing import Queue
import asyncio
import json
import logging
import websockets
import traceback
from handlers import all_handlers
CBS_URI = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger("mappy")
log.setLevel(logging.INFO)


def run(score_q, log_q):
    my_map = Map(score_q, log_q)
    asyncio.run(my_map.try_map())


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

    def map_loop(self):
        try_again = True
        while try_again:
            log.info("Trying Map Loop")
            try_again = self.try_map()
            log.info(f"Try Map finished and returned {try_again}")

    async def try_map(self):
        log.info("Trying map")
        try:
            async with websockets.connect(CBS_URI, ssl=True) as ws:
                while True:
                    message = await ws.recv()
                    await self.attempt_all(message, ws)
        except (websockets.exceptions.ConnectionClosedOK) as e:
            log.info("Closed for normal reasons")
            log.info(e)
            return True

        except (
                websockets.exceptions.InvalidStatusCode,
                websockets.exceptions.ConnectionClosedError,
        ) as e:
            log.info("Closed for BAD reasons")
            log.info(e)
            return False
        except (KeyboardInterrupt, BaseException) as e:
            log.info("Closed for other exception")
            log.info(e)
            # log.info(traceback.format_exc())
            return False


if __name__ == "__main__":
    run(Queue(), Queue())
