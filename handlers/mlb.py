import logging
from handlers.league import League
from handlers.score import Score
log = logging.getLogger("mappy")


class MLBLeague(League):
    @property
    def league_name(self):
        return "mlb"

    async def update(self, obj, ws):
        # MLB game list changes throughout the day, so the
        # default update action of unsubscribing is bad.
        # keep looking for active games instead
        await self.set_state(obj, ws)


class MLBScore(Score):
    @property
    def league_name(self):
        return "mlb"

    async def handle(self, obj, ws):
        teams = obj.get("body", [])
        for team in teams:
            team_id = team["abbr"]
            score = int(team["batting"]["runs"])
            self.record_score(team_id, score)
