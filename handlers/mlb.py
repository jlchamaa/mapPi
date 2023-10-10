import logging
from handlers.base import Handler
log = logging.getLogger("mappy")


class MLBScoreboard(Handler):
    def is_relevant(self, obj):
        return (
            obj.get("topic") == "/mlb/scoreboard"
            and obj.get("eventType") in ["update", "setState"]
        )

    async def handle(self, obj, ws):
        log.info("MLB handle")
        games = obj.get("body", {}).get("games", [])
        for game in games:
            abbr =game.get("abbr")
            log.info(abbr)
            log.info("needa subscribe tho")
            self.log_q({"msg": abbr})
        

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
