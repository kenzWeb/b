from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from .serializers import (
    RegistrationSerializer, CourseSerializer, LessonSerializer, EnrollmentSerializer
)
from courses.models import Course
from students.models import Enrollment
import uuid
import datetime

class RegistrationView(views.APIView):
    """регистрации пользователей"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        
        
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True}, status=status.HTTP_201_CREATED)

class AuthView(views.APIView):
    """авторизации"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            
            return Response({
                "message": "Invalid data",
                "errors": {"email": ["Invalid data"]} 
            }, status=422)

        user = authenticate(username=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
             return Response({
                "message": "Invalid data",
                "errors": {"email": ["Invalid credentials"]} 
            }, status=422)

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с курсами"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """Получение детальной информации о курсе"""
        
        instance = self.get_object()
        lessons = instance.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response({"data": serializer.data})

    @action(detail=True, methods=['post'], url_path='buy')
    def buy(self, request, pk=None):
        """Действие для покупки (записи на) курс"""
        course = self.get_object()
        today = timezone.now().date()
        
        
        if today >= course.start_date or today > course.end_date:
            return Response({"message": "Course unavailable"}, status=400) 

        
        order_id = uuid.uuid4().hex
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'order_id': order_id, 'status': 'pending'}
        )
        
        
        if not created and enrollment.status == 'success':
             return Response({"message": "Already enrolled"}, status=400)
        
        
        if not created:
            enrollment.order_id = order_id
            enrollment.save()

        pay_url = f"https://payment.provider/pay?order_id={order_id}"
        return Response({"pay_url": pay_url})

class PaymentWebhookView(views.APIView):
    """Вебхук для обработки статусов оплаты"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        order_id = request.data.get('order_id')
        status_val = request.data.get('status') 

        try:
            enrollment = Enrollment.objects.get(order_id=order_id)
            if status_val == 'success':
                enrollment.status = 'success'
            elif status_val == 'failed':
                enrollment.status = 'failed'
            enrollment.save()
        except Enrollment.DoesNotExist:
            pass 
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с записями текущего пользователя"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

    
    
    
    def list(self, request, *args, **kwargs):
        """Получение списка записей"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data}) 

    def retrieve(self, request, *args, **kwargs):
        """Отмена записи"""
        
        try:
            instance = self.get_object()
            if instance.status in ['pending', 'failed']:
                 instance.delete()
                 return Response({"status": "success"})
            else:
                 return Response({"status": "was payed"}, status=418)
        except Exception:
             raise 

class MyOrdersView(views.APIView):
    """получения списка заказов"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True, context={'request': request})
        return Response({"data": serializer.data})

class CancelOrderView(views.APIView):
    """отмены заказа"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            enrollment = Enrollment.objects.get(pk=pk, user=request.user)
            if enrollment.status in ['pending', 'failed']:
                enrollment.delete()
                return Response({"status": "success"})
            else:
                return Response({"status": "was payed"}, status=418)
        except Enrollment.DoesNotExist:
            return Response({"message": "Not found"}, status=404)

class CheckCertificateView(views.APIView):
    """проверки сертификата"""
    permission_classes = [permissions.AllowAny] 

    def post(self, request):
        
        
        cert_num = request.data.get('sertikate_number')
        if not cert_num:
             return Response({"status": "failed"}, status=200)

        
        if cert_num.endswith('1'):
            return Response({"status": "success"})
        else:
            return Response({"status": "failed"})
