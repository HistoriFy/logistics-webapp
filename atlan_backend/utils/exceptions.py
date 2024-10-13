from rest_framework.exceptions import APIException
from rest_framework import status

class CustomException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred.'
    default_code = 'error'

class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'The request is invalid or malformed.'
    default_code = 'bad_request'

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = {'detail': self.default_detail}
        if code is not None:
            self.default_code = code

class Unauthorized(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'You are not authorized to access this resource.'
    default_code = 'unauthorized'

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = {'detail': self.default_detail}
        if code is not None:
            self.default_code = code