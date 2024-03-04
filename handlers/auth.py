from handlers.base import Handler
ACCESS_TOKEN = "64d1553ce024ab863adf69cff277b1f2ed75d961"


class Auth(Handler):
    def is_relevant(self, obj):
        return obj.get("auth") == "ready"

    async def handle(self, message, ws):
        req = {
            "cmd": "login",
            "access_token": ACCESS_TOKEN,
        }
        await ws.send(self.tostring(req))
