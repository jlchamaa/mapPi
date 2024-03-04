import logging
from handlers.league import League
from handlers.score import Score
log = logging.getLogger("mappy")


class NBALeague(League):
    @property
    def league_name(self):
        return "nba"


class NBAScore(Score):
    def is_relevant(self, obj):
        return (
            obj.get("topic", "").startswith("/nba/gametracker")
            and obj.get("eventType") == "update"
        )

    async def handle(self, obj, ws):
        teams = obj.get("body", [])
        for team in teams:
            name = team["abbr"]
            score = int(team["stats"]["points"])
            self.record_score("nba", name, score)
