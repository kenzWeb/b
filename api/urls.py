"""
Маршрутизация API.
Содержит пути для регистрации, авторизации, курсов, заказов и проверки сертификатов.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegistrationView, AuthView, CourseViewSet, PaymentWebhookView,
    MyOrdersView, CancelOrderView, CheckCertificateView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
    path('registr', RegistrationView.as_view(), name='registr'),
    path('auth', AuthView.as_view(), name='auth'),
    path('payment-webhook', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('orders', MyOrdersView.as_view(), name='orders-list'),
    path('orders/<int:pk>', CancelOrderView.as_view(), name='orders-cancel'),
    
    
    
    path('check-sertificate', CheckCertificateView.as_view(), name='check-certificate'),
    path('', include(router.urls)),
]
