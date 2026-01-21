from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course, Lesson
from students.models import Enrollment
import datetime
import uuid

User = get_user_model()

class CriteriaTests(APITestCase):
    """
    Тесты для проверки критериев задания "Модуль Б".
    """

    def setUp(self):
        self.user_data = {
            "email": f"test_{uuid.uuid4().hex}@example.com",
            "password": "Password1!#",
        }
        self.course = Course.objects.create(
            name="Test Course",
            description="Desc",
            hours=10,
            price=1000,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=10)
        )

    def test_registration(self):
        """Проверка регистрации пользователя."""
        url = '/school-api/registr'
        # Try to guess URL or use hardcoded if reverse fails or is unknown
        # Based on urls.py inspection it is likely just 'registr' in api.urls
        # Let's use the hardcoded path from inspection to be safe or investigate urls.py names?
        # Inspection showed: path('school-api/', include('api.urls'))
        # api/urls.py usually has path('registr', ...)
        
        response = self.client.post('/school-api/registr', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_auth_and_token(self):
        """Проверка авторизации и получения токена."""
        self.client.post('/school-api/registr', self.user_data)
        response = self.client.post('/school-api/auth', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        return response.data['token']

    def test_course_list_pagination(self):
        """Проверка списка курсов и пагинации."""
        token = self.test_auth_and_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Create additional courses to test pagination (page_size=5)
        for i in range(6):
            Course.objects.create(
                name=f"C{i}", hours=1, price=100, 
                start_date=datetime.date.today(), end_date=datetime.date.today()
            )

        response = self.client.get('/school-api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('pagination', response.data)
        # Should be 5 per page
        self.assertLessEqual(len(response.data['data']), 5)

    def test_lesson_limit_validation(self):
        """Проверка ограничения на 5 уроков."""
        for i in range(5):
            Lesson.objects.create(course=self.course, name=f"L{i}", hours=1, video_link="https://super-tube.cc/video/1")
        
        l6 = Lesson(course=self.course, name="L6", hours=1, video_link="https://super-tube.cc/video/1")
        try:
            l6.full_clean()
            l6.save()
            failed = False
        except Exception:
            failed = True
        self.assertTrue(failed, "Должно быть запрещено создание более 5 уроков")

    def test_video_link_validation(self):
        """Проверка валидации ссылки на видео (super-tube.cc)."""
        l = Lesson(course=self.course, name="Bad Link", hours=1, video_link="https://youtube.com/watch?v=123")
        with self.assertRaises(Exception): # ValidationError usually
            l.full_clean()
    
    def test_deletion_protection(self):
        """Нельзя удалить курс/урок, если есть студенты."""
        User.objects.create_user(username="s1", email="s1@test.com", password="P1")
        # Enrollment needed logic check (assumes Enrolled student exists)
        # We need an enrollment.
        u = User.objects.get(username="s1")
        Enrollment.objects.create(user=u, course=self.course, status='success')
        
        with self.assertRaises(Exception): # ValidationError from delete() method
            self.course.delete()

    def test_cancel_paid_course(self):
        """Нельзя отменить оплаченный курс (403)."""
        token = self.test_auth_and_token()
        client = self.client
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Enroll user
        u = User.objects.get(email=self.user_data['email'])
        enr = Enrollment.objects.create(user=u, course=self.course, status='success')
        
        # Try to delete/cancel via API
        # Need to know the URL. EnrollementViewSet usually at /school-api/enrollments/{id}/ ?
        # Based on inspection, we need to find the EnrollmentViewSet URL. 
        # Usually router registers it. Let's assume /school-api/enrollments/{id}/
        
        # Test DELETE or GET? 
        # views.py EnrollmentViewSet.retrieve says: "Отмена записи (по ID записи)."
        # It's a GET request to retrieve? No, retrieve is GET.
        # But the docstring says "Отмена записи". 
        # If the code implemented cancellation inside `retrieve`, that's weird but possible per "Module B" tasks sometimes.
        # Let's check views.py again.
        # views.py: def retrieve(self, request, *args, **kwargs): ... instance.delete() ...
        # Yes, it is GET /enrollments/{id}/ that triggers delete.
        
        url = f'/school-api/orders/{enr.id}' 
        
        response = client.get(url) 
        self.assertEqual(response.status_code, 403)

    def test_webhook_processing(self):
        """Обработка вебхука оплаты."""
        # Create pending enrollment
        u = User.objects.create_user(username="w@t.com", email="w@t.com", password="P1")
        order_id = "test_order_123"
        enr = Enrollment.objects.create(user=u, course=self.course, status='pending', order_id=order_id)
        
        webhook_data = {"order_id": order_id, "status": "success"}
        response = self.client.post('/school-api/payment-webhook', webhook_data) 
        
        enr.refresh_from_db()
        self.assertEqual(enr.status, 'success')
        
    def test_certificate_field(self):
        """Проверка наличия поля для сертификата."""
        user = User.objects.create_user(username="cert@test.com", email="cert@test.com", password="Password1!")
        enrollment = Enrollment.objects.create(user=user, course=self.course, status='success')
        self.assertTrue(hasattr(enrollment, 'certificate_number'))

