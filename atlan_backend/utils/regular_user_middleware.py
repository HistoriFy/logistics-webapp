import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from authentication.models import User

@database_sync_to_async
def get_user(token_key):
    try:
        payload = jwt.decode(token_key, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = User.objects.get(id=user_id)
        return user
    except (jwt.DecodeError, jwt.ExpiredSignatureError, User.DoesNotExist):
        return AnonymousUser()
    except Exception as e:
        print(f"Unexpected error in get_user: {str(e)}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            # Extract query parameters
            query_string = scope.get('query_string', b'').decode()
            params = dict(x.split('=') for x in query_string.split('&') if x)
            token = params.get('token')

            if token:
                # Authenticate user
                scope['user'] = await get_user(token)
            else:
                scope['user'] = AnonymousUser()

            # Call the inner application
            return await super().__call__(scope, receive, send)
        
        except Exception as e:
            print(f"Error in middleware: {str(e)}")
            scope['user'] = AnonymousUser()
            return await super().__call__(scope, receive, send)