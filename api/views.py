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
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True}, status=status.HTTP_201_CREATED)

class AuthView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            # Custom validation error structure manual
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
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # Override to return lessons
        instance = self.get_object()
        lessons = instance.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response({"data": serializer.data})

    @action(detail=True, methods=['post'], url_path='buy')
    def buy(self, request, pk=None):
        course = self.get_object()
        today = timezone.now().date()
        
        # Validation: cannot buy if started or ended
        # "нельзя записаться на курс, который уже начался или закончился"
        if today >= course.start_date or today > course.end_date:
            return Response({"message": "Course unavailable"}, status=400) # Spec doesn't define error code, 400 safe

        # Create Enrollment
        order_id = uuid.uuid4().hex
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'order_id': order_id, 'status': 'pending'}
        )
        
        # If already enrolled/paid?
        if not created and enrollment.status == 'success':
             return Response({"message": "Already enrolled"}, status=400)
        
        # If pending, we can update order_id or just return existing
        if not created:
            enrollment.order_id = order_id
            enrollment.save()

        pay_url = f"https://payment.provider/pay?order_id={order_id}"
        return Response({"pay_url": pay_url})

class PaymentWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        order_id = request.data.get('order_id')
        status_val = request.data.get('status') # 'success' | 'failed'

        try:
            enrollment = Enrollment.objects.get(order_id=order_id)
            if status_val == 'success':
                enrollment.status = 'success'
            elif status_val == 'failed':
                enrollment.status = 'failed'
            enrollment.save()
        except Enrollment.DoesNotExist:
            pass # Spec: Status 204 regardless
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

    # Spec: GET /orders (list)
    # Spec: GET /orders/{id} (cancel)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data}) # Spec wraps in "data"

    def retrieve(self, request, *args, **kwargs):
        # Implement Cancel logic
        try:
            instance = self.get_object()
            if instance.status in ['pending', 'failed']:
                 instance.delete()
                 return Response({"status": "success"})
            else:
                 return Response({"status": "was payed"}, status=418)
        except Exception:
             raise # Or 404

class MyOrdersView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True, context={'request': request})
        return Response({"data": serializer.data})

class CancelOrderView(views.APIView):
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
    permission_classes = [permissions.AllowAny] # Presumed public or internal

    def post(self, request):
        # Body: { sertikate_number: ... }
        # Note: Spec has typo "sertikate_number"
        cert_num = request.data.get('sertikate_number')
        if not cert_num:
             return Response({"status": "failed"}, status=200)

        # Logic: Ends with 1 valid, 2 invalid
        if cert_num.endswith('1'):
            return Response({"status": "success"})
        else:
            return Response({"status": "failed"})
