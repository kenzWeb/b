from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, PermissionDenied, NotAuthenticated
from rest_framework import status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        data = {
            "message": "Invalid fields",
            "errors": response.data if response else {}
        }
        return Response(data, status=422)

    if isinstance(exc, (PermissionDenied, NotAuthenticated)):
        
        �зации: Status code: 403".
        
        return Response({"message": "Forbidden for you"}, status=403)

    return response
