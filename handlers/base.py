from abc import ABC, abstractmethod
import json
import logging
import traceback
log = logging.getLogger("mappy")


class Handler(ABC):
    def __init__(self, score_q, log_q):
        self.score_q = score_q
        self.log_q = log_q
        self.extra_init()

    def extra_init(self):
        pass

    async def attempt(self, obj, ws):
        try:
            if self.is_relevant(obj):
                await self.handle(obj, ws)
        except BaseException:
            if not (isinstance(obj, dict) or isinstance(obj, list)):
                obj = str(obj)
            traceback.print_exc()
            log.info(type(obj))
            log.info(str(obj))

    def tostring(self, obj):
        for _ in range(2):
            obj = json.dumps(obj)
        return obj

    @abstractmethod
    def is_relevant(self, obj):
        raise NotImplementedError

    @abstractmethod
    async def handle(self, obj, ws):
        raise NotImplementedError
