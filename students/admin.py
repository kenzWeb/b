from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponse
from .models import Enrollment
import random
import requests 

SERVICE_HOST = "http://test" 

@admin.action(description='Распечатать сертификат')
def print_certificate(modeladmin, request, queryset):
    """Действие админ-панели для печати сертификата"""
    
    if queryset.count() != 1:
        modeladmin.message_user(request, "Пожалуйста, выберите ровно одну запись для печати сертификата.", level='error')
        return

    enrollment = queryset.first()
    
    if enrollment.status != 'success':
        modeladmin.message_user(request, "Сертификат можно распечатать только для оплаченных курсов.", level='error')
        return

    
    if not enrollment.certificate_number:
        
        service_part = "ABCDEF" 
        
        random_part = "".join([str(random.randint(0, 9)) for _ in range(5)]) + "1"
        
        full_number = service_part + random_part
        enrollment.certificate_number = full_number
        enrollment.save()
    
    
    
    html_content = f"""
    <html>
    <head>
        <title>Сертификат</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; border: 10px solid gold; padding: 50px; }}
            h1 {{ color: navy; }}
            .number {{ font-size: 20px; color: gray; }}
        </style>
    </head>
    <body onload="window.print()">
        <h1>Сертификат</h1>
        <p>Настоящим подтверждается, что</p>
        <h2>{enrollment.user.first_name} {enrollment.user.last_name} ({enrollment.user.email})</h2>
        <p>Успешно прошел(ла) курс</p>
        <h2>{enrollment.course.name}</h2>
        <p class="number">Номер сертификата: {enrollment.certificate_number}</p>
    </body>
    </html>
    """
    return HttpResponse(html_content)

class EnrollmentAdmin(admin.ModelAdmin):
    """Административная панель для управления записями студентов"""
    list_display = ('get_user_email', 'get_user_name', 'course', 'date', 'status')
    list_filter = ('course',)
    actions = [print_certificate]

    def get_user_email(self, obj):
        """Возвращает email пользователя."""
        return obj.user.email
    get_user_email.short_description = 'Email'

    def get_user_name(self, obj):
        """Возвращает полное имя пользователя."""
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'Имя'

admin.site.register(Enrollment, EnrollmentAdmin)
