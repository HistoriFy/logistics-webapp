from channels.routing import ProtocolTypeRouter, URLRouter

from regular_user.routing import websocket_urlpatterns as regular_user_websocket_urlpatterns
from driver.routing import websocket_urlpatterns as driver_websocket_urlpatterns

from utils.regular_user_middleware import JWTAuthMiddleware
from utils.driver_middleware import DriverJWTAuthMiddleware

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        # WebSocket connections for regular users
        URLRouter(
            regular_user_websocket_urlpatterns,
            middleware_stack=JWTAuthMiddleware 
        ),
        # WebSocket connections for drivers
        URLRouter(
            driver_websocket_urlpatterns,
            middleware_stack=DriverJWTAuthMiddleware
        ),
    ]),
})