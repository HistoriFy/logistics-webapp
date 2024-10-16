import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async

from authentication.models import Driver

@database_sync_to_async
def get_user(token_key):
    try:
        payload = jwt.decode(token_key, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = Driver.objects.get(id=user_id)
        return user
    except Exception:
        return AnonymousUser()

class DriverJWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return DriverJWTAuthMiddlewareInstance(scope, self)

class DriverJWTAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.scope = scope
        self.inner = middleware.inner

    async def __call__(self, receive, send):
        query_string = self.scope['query_string'].decode()
        params = dict(x.split('=') for x in query_string.split('&') if x)
        token = params.get('token', None)
        self.scope['user'] = await get_user(token)
        inner = self.inner(self.scope)
        return await inner(receive, send)
