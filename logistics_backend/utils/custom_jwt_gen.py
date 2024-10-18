import jwt
from django.conf import settings
from datetime import datetime, timedelta, timezone

def generate_jwt_token(user, user_type):
    payload = {
        "user_id": user.id,
        "user_type": user_type,
        "exp": datetime.now(timezone.utc)+ settings.ACCESS_TOKEN_LIFETIME,
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token
