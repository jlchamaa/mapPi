import logging
from handlers.base import League
log = logging.getLogger("mappy")


class MLBScoreboard(League):
    def is_relevant(self, obj):
        return (
            obj.get("topic") == "/mlb/scoreboard"
            and obj.get("eventType") in ["update", "setState"]
        )

    async def handle(self, obj, ws):
        if obj.get("eventType")  == "setState":
            await self.set_up(obj, ws)
        if obj.get("eventType")  == "update":
            await self.tear_down(obj, ws)

    async def set_up(self, obj, ws):
        log.info("MLB handle")
        games = obj.get("body", {}).get("games", [])
        for game in games:
            abbr =game.get("abbr")
            log.info(abbr)
            log.info("needa subscribe tho")
            if abbr not in self.topics: 
                self.topics.append(abbr)
                gt_topic = f"/mlb/gametracker/{abbr}/ts"
                await self.subscribe_topic(ws, gt_topic)
                self.log_q.put({"msg": f"Subscribed {gt_topic}"})
        
    async def tear_down(self, obj, ws):
        await self.unsubscribe_topic(ws, "/mlb/scoreboard")

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
