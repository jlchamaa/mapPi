#!/usr/bin/env python3.8
import asyncio
import websockets


async def hello():
    uri = "wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket"
    async with websockets.connect(uri, ssl=True) as ws:
        greeting = await ws.recv()
        print(greeting)

asyncio.get_event_loop().run_until_complete(hello())
