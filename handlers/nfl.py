import logging
from handlers.base import Handler
log = logging.getLogger("mappy")


class NFLHandler(Handler):
    def is_relevant(self, message):
        return True

    def handle(self, message, ws):
        log.info("NFL handle")
        
    def handle_nfl(self, data):
        self.logwrite("NFL Update")
        try:
            teams = re.search(r"_(\w{2,3})@(\w{2,3})", data["topic"]).groups()
            if "scores" in data["body"]:
                score_list = data["body"]["scores"]
                if len(score_list) > 0:
                    score_obj = score_list[-1]
                else:
                    return
            else:
                score_obj = data["body"][0]
            r = self.sb.record_score("nfl", teams[0], int(score_obj["away_score"]))
            self.logwrite(r)
            r = self.sb.record_score("nfl", teams[1], int(score_obj["home_score"]))
            self.logwrite(r)
            # await self.emit(self.Updatemessage(self, "nfl"))
        except Exception as e:
            self.logwrite(json.dumps(data, indent=2, sort_keys=True))
            self.logwrite("Problem in the NFL")
            self.logwrite(e)
