from abc import abstractmethod
from handlers.base import Handler
import logging
log = logging.getLogger("mappy")


class League(Handler):
    def extra_init(self):
        self.topics = []

    @property
    @abstractmethod
    def league_name(self):
        raise NotImplementedError

    def is_relevant(self, obj):
        return (
            obj.get("topic") == f"/{self.league_name}/scoreboard"
            and obj.get("eventType") in ["update", "setState"]
        )

    async def handle(self, obj, ws):
        if obj.get("eventType") == "setState":
            await self.set_state(obj, ws)
        if obj.get("eventType") == "update":
            await self.update(obj, ws)

    async def set_state(self, obj, ws):
        games = obj.get("body", {}).get("games", [])
        for game in games:
            abbr = game.get("abbr")
            if abbr is None:
                # self.log_q.put(obj)
                log.info(obj)
                return
            if abbr not in self.topics:
                self.topics.append(abbr)
                gt_topic = f"/{self.league_name}/gametracker/{abbr}/ts"
                await self.subscribe_topic(ws, gt_topic)

    async def update(self, obj, ws):
        # await self.unsubscribe_topic(ws, f"/{self.league_name}/scoreboard")
        pass

    async def subscribe_topic(self, ws, topic):
        req = {"cmd": "subscribe", "topics": [topic]}
        # self.log_q.put(req)
        log.info(req)
        await ws.send(self.tostring(req))

    async def unsubscribe_topic(self, ws, topic):
        req = {"cmd": "unsubscribe", "topics": [topic]}
        # self.log_q.put(req)
        log.info(req)
        await ws.send(self.tostring(req))
