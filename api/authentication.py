from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    """
    Кастомная аутентификация по токену.
    Использует ключевое слово 'Bearer' вместо стандартного 'Token'.
    """
    keyword = 'Bearer'
