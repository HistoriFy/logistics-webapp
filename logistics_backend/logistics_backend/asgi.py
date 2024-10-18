import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logistics_backend.settings")

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from logistics_backend.routing import application as websocket_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": websocket_application,
})
