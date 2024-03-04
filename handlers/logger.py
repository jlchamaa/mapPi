from handlers.base import Handler


class Logger(Handler):
    def is_relevant(self, obj):
        return True

    async def handle(self, obj, ws):
        self.log_q.put(obj)
