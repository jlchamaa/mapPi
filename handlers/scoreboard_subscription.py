from handlers.base import Handler


class ScoreboardSubscription(Handler):
    def is_relevant(self, obj):
        return obj.get("authorized") == "ok"

    async def handle(self, message, ws):
        req = {
            "cmd": "subscribe",
            "topics": [
                "/mlb/scoreboard",
                "/nfl/scoreboard",
                "/nba/scoreboard",
            ]}
        self.log_q.put(req)
        await ws.send(self.tostring(req))
