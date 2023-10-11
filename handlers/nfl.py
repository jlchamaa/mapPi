import logging
from handlers.base import League, Score
log = logging.getLogger("mappy")


class NFLScoreboard(League):
    def is_relevant(self, obj):
        return (
            obj.get("topic") == "/nfl/scoreboard"
            and obj.get("eventType") in ["update", "setState"]
        )

    async def handle(self, obj, ws):
        log.info("NFL scoreboard handle")
        games = obj.get("body", {}).get("games", [])
        for game in games:
            abbr =game.get("abbr")
            log.info(abbr)
            log.info("needa subscribe tho")
            if abbr not in self.topics: 
                self.log_q.put({"msg": f"We need: {abbr}"})
                self.topics.append(abbr)
            else:
                self.log_q.put({"msg": f"We don't need: {abbr}"})


        
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


class NFLScore(Score):
    def is_relevant(self, obj):
        topic = obj.get("topic")
        return topic.startswith("/nfl/") and "@" in topic

    def handle(self, obj, ws):
        log.info("NFL Score")
