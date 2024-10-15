from channels.routing import ProtocolTypeRouter, URLRouter

from regular_user.routing import websocket_urlpatterns
from utils.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    'websocket': JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})