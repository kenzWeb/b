from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Использует email в качестве основного идентификатора (USERNAME_FIELD).
    """
    email = models.EmailField(unique=True, verbose_name='Email Address')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        """Возвращает строковое представление пользователя (email)."""
        return self.email
