import logging
from handlers.base import League, Score
log = logging.getLogger("mappy")


class NBAScoreboard(League):
    def is_relevant(self, obj):
        return (
            obj.get("topic") == "/nba/scoreboard"
            and obj.get("eventType") in ["update", "setState"]
        )

    async def handle(self, obj, ws):
        if obj.get("eventType")  == "setState":
            await self.set_up(obj, ws)
        if obj.get("eventType")  == "update":
            await self.tear_down(obj, ws)

    async def set_up(self, obj, ws):
        games = obj.get("body", {}).get("games", [])
        for game in games:
            abbr =game.get("abbr")
            if abbr not in self.topics: 
                self.topics.append(abbr)
                gt_topic = f"/nba/gametracker/{abbr}/ts"
                await self.subscribe_topic(ws, gt_topic)
                self.log_q.put({"msg": f"Subscribed {gt_topic}"})
                log.info(f"Subscribed {gt_topic}")
        
    async def tear_down(self, obj, ws):
        await self.unsubscribe_topic(ws, "/nba/scoreboard")


class NBAScore(Score):
    def is_relevant(self, obj):
        return (
            obj.get("topic", "").startswith("/nba/gametracker")
            and obj.get("eventType") == "update"
        )

    async def handle(self, obj, ws):
        teams = obj.get("body", [])
        for team in teams:
            name = team.get("abbr")
            score = int(team["stats"].get("points"))
            self.record_score("nba", name, score)
            self.log_q.put({name: score})
