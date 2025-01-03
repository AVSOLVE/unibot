import json

from channels.generic.websocket import AsyncWebsocketConsumer


class LiveDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the live_data group
        self.group_name = "live_data"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when the WebSocket closes
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Handle incoming WebSocket messages if needed
        pass

    # Receive message from the group
    async def live_data_message(self, event):
        # Send message to WebSocket
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
