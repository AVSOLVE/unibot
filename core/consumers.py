import json

from channels.generic.websocket import WebsocketConsumer


class LiveDataConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket connected!")

    def disconnect(self, close_code):
        print("WebSocket disconnected.")

    def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Message received: {data['message']}")
        # Echo the message back to the client
        self.send(
            text_data=json.dumps({"message": f"Server received: {data['message']}"})
        )
