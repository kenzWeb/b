from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    """аутентификация по токену"""
    keyword = 'Bearer'
