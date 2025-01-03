import json

from channels.generic.websocket import AsyncWebsocketConsumer


class LiveDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("live_data", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("live_data", self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Handle incoming WebSocket messages if needed
        pass

    # Receive message from the group
    async def live_data_message(self, event):
        # Send message to WebSocket
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
