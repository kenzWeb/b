from django.db import models
from django.conf import settings
from courses.models import Course

class Enrollment(models.Model):
    """
    Модель записи студента на курс.
    Хранит статус оплаты, дату записи, ID заказа и номер сертификата.
    """
    STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('success', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата записи")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус оплаты")
    order_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID заказа")
    certificate_number = models.CharField(max_length=12, blank=True, null=True, verbose_name="Номер сертификата")

    def __str__(self):
        """Возвращает строковое представление записи (email студента - название курса)."""
        return f"{self.user.email} - {self.course.name}"
