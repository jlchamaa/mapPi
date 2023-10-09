import logging
from handlers.base import Handler
log = logging.getLogger("mappy")


class MLBHandler(Handler):
    def is_relevant(self, message):
        return True

    def handle(self, message, ws):
        log.info("MLB handle")
        

    async def handle_mlb(self, data, ws):
        return
        try:
            et = data["eventType"]
            if et != "update":
                return
            for entry in data["body"]:
                team_id = entry["abbr"]
                score = int(entry["batting"]["runs"])
                r = self.sb.record_score("mlb", team_id, score)
                self.logwrite(r)
                # await self.emit(self.Updatemessage(self, "mlb"))
        except Exception as e:
            self.logwrite("Problem in the MLB")
            self.logwrite(e)
            self.logwrite(json.dumps(data, indent=2))
