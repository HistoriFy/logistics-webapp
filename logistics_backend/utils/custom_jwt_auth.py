from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework import exceptions
import jwt
from django.conf import settings

from authentication.models import User, Driver, FleetOwner

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                return None
        except ValueError:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user_type = payload.get("user_type")

            if user_type == "User":
                user = User.objects.get(id=user_id)
            elif user_type == "Driver":
                user = Driver.objects.get(id=user_id)
            elif user_type == "FleetOwner":
                user = FleetOwner.objects.get(id=user_id)
            else:
                raise exceptions.AuthenticationFailed("Invalid user type")

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed("Error decoding token")
        except (User.DoesNotExist, Driver.DoesNotExist, FleetOwner.DoesNotExist):
            raise exceptions.AuthenticationFailed("User not found")

        user.user_type = user_type

        return (user, token)

class IsFleetOwner(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "user_type", None) == "FleetOwner"

class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "user_type", None) == "Driver"

class IsRegularUser(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "user_type", None) == "User"
