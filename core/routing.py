from django.urls import path

from .consumers import LiveDataConsumer

websocket_urlpatterns = [
    path("ws/live-data/", LiveDataConsumer.as_asgi()),
]
