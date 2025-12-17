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
        # Spec: Status code 403, { "message": "Forbidden for you" }
        # Note: NotAuthenticated usually returns 401. Prompt says "При попытке доступа без авторизации: Status code: 403".
        # So I should map 401/403 to 403 with this message.
        return Response({"message": "Forbidden for you"}, status=403)

    return response
