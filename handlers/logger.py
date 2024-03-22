from datetime import datetime
from handlers.base import Handler
from datetime import datetime
from json import dump
file = "playback.log"


class Logger(Handler):
    def is_relevant(self, obj):
        return True

    async def handle(self, obj, ws):
        obj["z_timestamp"] = datetime.now().strftime("%c")
        with open(file, "a") as f:
            dump(obj, f, indent=2, sort_keys=True)
            f.write(",\n")
            # self.log_q.put(obj)
