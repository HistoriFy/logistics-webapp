from django.urls import re_path
from .consumers import BookingStatusConsumer

websocket_urlpatterns = [
    re_path(r"ws/bookings/", BookingStatusConsumer.as_asgi()),
]
