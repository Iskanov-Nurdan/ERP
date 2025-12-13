import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SalesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("sales", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("sales", self.channel_name)

    async def event(self, event):
        await self.send(text_data=json.dumps(event["data"]))
