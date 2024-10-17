from rest_framework import status


class CustomException(Exception):
    def __init__(self, message=None):
        if message is None:
            message = self.default_message
            
        self.message = message
        super().__init__(self.message)
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = 'An error occured'


class BadRequest(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'The request is invalid or malformed'
    
    
class Unauthorized(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = 'You are not authorized to access this resource'