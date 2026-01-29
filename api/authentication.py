from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    """Кастомная аутентификация по токену"""
    keyword = 'Bearer'
