from datetime import datetime, timedelta
import json
from traceback import print_exc
from typing import Any, Dict, Optional
from functools import wraps
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import User, Driver, FleetOwner
from utils.exceptions import BadRequest


'''
---DECORATOR---
Used to validate the token in the request headers
'''
def validate_token(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = ['User', 'Driver', 'FleetOwner']  # Default: allow all roles
    
    def decorator(func):
        @wraps(func)
        def wrapper_func(request, *args, **kwargs):
            try:
                jwt_authenticator = JWTAuthentication()
                
                try:
                    token = request.headers.get('Authorization').split(' ')[1]
                    validated_token = jwt_authenticator.get_validated_token(token)
                    user = jwt_authenticator.get_user(validated_token)
                except Exception as e:
                    return response_obj(success=False, message='Invalid or expired token', status_code=status.HTTP_401_UNAUTHORIZED)

                request.user = user

                # Role-based access control
                if 'User' in allowed_roles and User.objects.filter(id=user.id).exists():
                    return func(request, *args, **kwargs)
                if 'Driver' in allowed_roles and Driver.objects.filter(id=user.id).exists():
                    return func(request, *args, **kwargs)
                if 'FleetOwner' in allowed_roles and FleetOwner.objects.filter(id=user.id).exists():
                    return func(request, *args, **kwargs)

                # If none of the allowed roles matched, return access denied
                return response_obj(success=False, message='Access denied: Unauthorized user group', status_code=status.HTTP_403_FORBIDDEN)

            except Exception as e:
                return response_obj(success=False, message='An error occurred', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error=e)

        return wrapper_func
    return decorator

def response_obj(success=True, message='', status_code=200, data=None, error=''):
    data = {
        "success": success,
        "message": message,
        "data": data if data else {}
    }
    if error:
        data['error'] = str(error)
    
    return Response(data, status=status_code)

       
def response_obj(success=True, message='', status_code=200, data={}, error=''):
    if(not error == ''):
        print_exc(error)
        
    data = {
        "success": success,
        "message": message,
        "data": data
    }
    return Response(data, status=status_code)


'''
Get the value of a key from a serializer's validated data
Used to ensure that we get a default value if the key is not present in the validated data
''' 
def get_serialized_data(serializer, key, default=''):
    if key in serializer.validated_data:
        return serializer.validated_data[key]
    return default


'''
---DECORATOR---
When wrapped on a function in a view, one can simply return a dictionary or a tuple of dictionary and status code
'''
def format_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
            
        if isinstance(result, Exception):
            raise result
        try:
            if isinstance(result, tuple) and len(result) == 2:
                response_body, status_code = result
                return APIResponse(data=response_body, status_code=status_code).response()
            
            return APIResponse(data=result).response()
        
        except Exception as e:
            return APIResponse(success=False, status_code=500, error=e).response()
    
    return wrapper


'''
Custom Response Class to format the response in a consistent manner
'''
class APIResponse:
    def __init__(self, success: bool = True, status_code: int = 200, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None):
        self.success = success
        self.status_code = status_code
        self.data = data or {}
        self.error = error

    def response(self, correlation_id: Optional[str] = None) -> JsonResponse:   
        response_data: Dict[str, Any] = {
            "success": self.success,
            "data": self.data
        }

        if self.error:
            response_data["error"] = {
                "code": self.error.__class__.__name__,
                "message": str(self.error.message) if hasattr(self.error, "message") else 'An error occurred',
                "details": str(self.error.details) if hasattr(self.error, "details") else str(self.error)
            }
        else :
            response_data["error"] = {
                "code": "",
                "message": "",
                "details": ""
            }

        if correlation_id:
            response_data["correlation_id"] = correlation_id


        return JsonResponse(response_data, status=self.status_code)

    def __str__(self) -> str:
        return f"APIResponse(success={self.success}, status_code={self.status_code}, data={self.data}, error={self.error})"



'''
Custom Serializer class to inherit from to handle validation errors
'''
class BaseSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            error_messages = [
                f"{key} - {error}" if key != "non_field_errors" else error
                for key, errors in exc.detail.items()
                for error in errors
            ]
            raise BadRequest(json.dumps(error_messages))