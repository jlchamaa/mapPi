from abc import ABC, abstractmethod
from handlers.base import Handler
import logging
log = logging.getLogger("mappy")


class League(Handler, ABC):
    def extra_init(self):
        self.topics = set()
        self.sb_topic = f"/{self.league_name}/scoreboard"

    @property
    @abstractmethod
    def league_name(self):
        raise NotImplementedError

    def _is_scoreboard_event(self, obj):
        return (
            obj.get("topic") == self.sb_topic
            and obj.get("eventType") in ["update", "setState"]
        )

    def _is_auth_event(self, obj):
        return obj.get("authorized") == "ok"

    def is_relevant(self, obj):
        return (
            self._is_auth_event(obj)
            or self._is_scoreboard_event(obj)
        )

    async def handle(self, obj, ws):
        if self._is_auth_event(obj):
            await self.subscribe_topic(ws, self.sb_topic)
        elif obj.get("eventType") == "setState":
            await self.set_state(obj, ws)
        elif obj.get("eventType") == "update":
            await self.update(obj, ws)
        else:
            log.info(obj)
            raise ValueError("Can't handle invalid request in league")

    async def set_state(self, obj, ws):
        games = obj.get("body", {}).get("games", [])
        for game in games:
            game_id = game.get("abbr", None)
            if game_id is not None and game_id not in self.topics:
                self.topics.add(game_id)
                gt_topic = f"/{self.league_name}/gametracker/{game_id}/ts"
                await self.subscribe_topic(ws, gt_topic)

    async def update(self, obj, ws):
        await self.unsubscribe_topic(ws, f"/{self.league_name}/scoreboard")

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
