import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from authentication.models import Driver

@database_sync_to_async
def get_driver(token_key):
    try:
        # Decode the JWT token
        payload = jwt.decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
        driver_id = payload["user_id"]

        # Fetch the driver with the provided ID
        driver = Driver.objects.get(id=driver_id)
        return driver
    except (jwt.DecodeError, jwt.ExpiredSignatureError, Driver.DoesNotExist):
        return AnonymousUser()
    except Exception as e:
        print(f"Unexpected error in get_driver: {str(e)}")
        return AnonymousUser()

class DriverJWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            # Extract the query parameters from the scope's query_string
            query_string = scope.get("query_string", b"").decode()
            params = dict(x.split("=") for x in query_string.split("&") if x)
            token = params.get("token")

            if token:
                # Authenticate the driver if the token is available
                scope["user"] = await get_driver(token)
            else:
                # Assign AnonymousUser if no token is present
                scope["user"] = AnonymousUser()

            # Call the inner application (super) with the updated scope
            return await super().__call__(scope, receive, send)

        except Exception as e:
            print(f"Error in DriverJWTAuthMiddleware: {str(e)}")
            scope["user"] = AnonymousUser()
            return await super().__call__(scope, receive, send)
