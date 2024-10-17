from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from regular_user.routing import websocket_urlpatterns as regular_user_websocket_urlpatterns
from driver.routing import websocket_urlpatterns as driver_websocket_urlpatterns

from utils.regular_user_middleware import JWTAuthMiddleware
from utils.driver_middleware import DriverJWTAuthMiddleware

def print_paths(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        print(f"{prefix}{pattern.pattern}")

regular_user_application = JWTAuthMiddleware(
    URLRouter(regular_user_websocket_urlpatterns)
)

driver_application = DriverJWTAuthMiddleware(
    URLRouter(driver_websocket_urlpatterns)
)

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        re_path(r'^regular_user/', regular_user_application),
        re_path(r'^driver/', driver_application),
    ]),
})

# print("Regular User WebSocket Paths:")
# print_paths(regular_user_websocket_urlpatterns, 'regular_user/')

# print("Driver WebSocket Paths:")
# print_paths(driver_websocket_urlpatterns, 'driver/')