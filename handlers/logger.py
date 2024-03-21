from handlers.base import Handler
from datetime import datetime
from json import dump
file = "playback.log"


class Logger(Handler):
    def is_relevant(self, obj):
        return True

    async def handle(self, obj, ws):
        with open(file, "a") as f:
            dump(obj, f, indent=2)
            f.write(",\n")
            # self.log_q.put(obj)
