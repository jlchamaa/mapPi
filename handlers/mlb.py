import logging
from handlers.base import League
from handlers.score import Score
log = logging.getLogger("mappy")


class MLBLeague(League):
    @property
    def league_name(self):
        return "mlb"


class MLBScore(Score):
    @property
    def league_name(self):
        return "mlb"

    async def handle(self, obj, ws):
        return
        # try:
        #     et = data["eventType"]
        #     if et != "update":
        #         return
        #     for entry in data["body"]:
        #         team_id = entry["abbr"]
        #         score = int(entry["batting"]["runs"])
        #         r = self.sb.record_score("mlb", team_id, score)
        #         self.logwrite(r)
        #         # await self.emit(self.Updatemessage(self, "mlb"))
        # except Exception as e:
        #     self.logwrite("Problem in the MLB")
        #     self.logwrite(e)
        #     self.logwrite(json.dumps(data, indent=2))
