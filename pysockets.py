#!/usr/bin/env python3
from datetime import datetime
import asyncio
import json
import logging
import sys
import websockets
from handlers import all_handlers
CBS_URI = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT)
log = logging.getLogger("mappy")
log.setLevel(logging.INFO)


def run():
    my_map = Map()
    try:
        result = asyncio.run(my_map.try_map())
    except (KeyboardInterrupt, asyncio.CancelledError):
        # these exceptions are somehow uncatchable inside of run.
        # problem described in try_map()
        result = 4

    log.info(f"We got this result: {result}!")
    return result


def destring(obj):
    obj = obj[2:-1]
    obj = json.loads(obj)
    obj = json.loads(obj)
    return obj


class Map():
    def __init__(self):
        self.handlers = self.build_handler(
    )

    def build_handler(self):
        return [h() for h in all_handlers]

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
                        log.info("Closing because a new day has sprung!")
                        return 0
            return 1

        except websockets.WebSocketException as e:
            log.info("Closed for websocket reasons")
            log.info(e)
            return 2

        except BaseException as e:
            log.info("Closed for other exception")
            log.info(type(e))
            return 3


if __name__ == "__main__":
    result = run()
    log.info(f"Sys.exit with: {result}!")
    sys.exit(result)
