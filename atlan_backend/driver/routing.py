from django.urls import re_path
from .consumers import DriverBookingConsumer, DriverAvailableBookingsConsumer

websocket_urlpatterns = [
    re_path(r'ws/driver/bookings/$', DriverBookingConsumer.as_asgi()),
    re_path(r'ws/driver/available_bookings/$', DriverAvailableBookingsConsumer.as_asgi()),
]