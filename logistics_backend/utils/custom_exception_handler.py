from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ValidationError

from .exceptions import CustomException

def custom_exception_handler_function(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            "success": False,
            "data": {},
            "error": {
                "code": response.status_code,
                "message": exc.__class__.__name__,
                "details": str(exc.detail) if hasattr(exc, "detail") else str(exc)
            }
        }, status=response.status_code)

    if isinstance(exc, CustomException):
        return Response({
            "success": False,
            "data": {},
            "error": {
                "code": exc.status_code,
                "message": exc.__class__.__name__,
                "details": exc.message
            }
        }, status=exc.status_code)

    if isinstance(exc, ValidationError):
        return Response({
            "success": False,
            "data": {},
            "error": {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "ValidationError",
                "details": exc.message_dict
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "success": False,
        "data": {},
        "error": {
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "InternalServerError",
            "details": str(exc)
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
