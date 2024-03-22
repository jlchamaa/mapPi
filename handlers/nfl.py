import logging
from handlers.league import League
from handlers.score import Score
log = logging.getLogger("mappy")


class NFLLeague(League):
    @property
    def league_name(self):
        return "nfl"


class NFLScore(Score):
    @property
    def league_name(self):
        return "nfl"

    async def handle(self, obj, ws):
        teams = obj.get("body", [])
        for team in teams:
            abbr = team["abbr"]
            score = int(team["total_points"])
            self.record_score("nfl", abbr, score)
