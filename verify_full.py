import os
import django
import requests
import json
import datetime
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course, Lesson
from users.models import User
from students.models import Enrollment
from students.admin import print_certificate

BASE_URL = "http://127.0.0.1:8000/school-api"

def create_test_data():
    print("--- Creating Test Data ---")
    
    Course.objects.all().delete()
    User.objects.filter(email="student@example.com").delete()
    
    
    img_io = BytesIO()
    
    
    
    img = Image.new('RGB', (500, 500), color = 'red')
    img.save(img_io, format='JPEG')
    img_content = img_io.getvalue()
    
    file = SimpleUploadedFile("test_course.jpg", img_content, content_type="image/jpeg")

    
    course = Course.objects.create(
        name="Backend Development",
        description="Learn Django",
        hours=10,
        price=500.00,
        start_date=datetime.date.today() + datetime.timedelta(days=1),
        end_date=datetime.date.today() + datetime.timedelta(days=30),
        img=file
    )
    print(f"Created Course: {course.name} (ID: {course.id})")
    
    
    
    
    
    for i in range(1, 4):
        Lesson.objects.create(
            course=course,
            name=f"Lesson {i}",
            text_content=f"Content for lesson {i}",
            video_link="https://super-tube.cc/video/v23189",
            hours=2
        )
    print(f"Created 3 lessons for course {course.id}")
    
    return course.id

def test_flow(course_id):
    session = requests.Session()
    
    
    print("\n--- 2. Register Student ---")
    reg_data = {
        "email": "student@example.com",
        "password": "Password1!"
    }
    r = session.post(f"{BASE_URL}/registr", json=reg_data)
    print(f"Status: {r.status_code} (Expected 201)")
    if r.status_code != 201:
        print(f"Error: {r.text}")
        return

    
    print("\n--- 3. Auth Student ---")
    auth_data = reg_data
    r = session.post(f"{BASE_URL}/auth", json=auth_data)
    print(f"Status: {r.status_code} (Expected 200)")
    token = r.json().get('token')
    headers = {"Authorization": f"Bearer {token}"}
    print("Got Token.")

    
    print("\n--- 4. List Courses ---")
    r = session.get(f"{BASE_URL}/courses", headers=headers)
    print(f"Status: {r.status_code}")
    data = r.json().get('data', [])
    print(f"Found {len(data)} courses.")
    if len(data) > 0:
        print(f"First Course: {data[0]['name']}")

    
    print(f"\n--- 5. Course Details (ID: {course_id}) ---")
    r = session.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
    print(f"Status: {r.status_code}")
    try:
        lessons = r.json().get('data', [])
        print(f"Found {len(lessons)} lessons.")
    except Exception as e:
        print(f"JSON Error: {e}")
        print(f"Response Text: {r.text[:2000]}")
        return

    
    print(f"\n--- 6. Buy Course (ID: {course_id}) ---")
    r = session.post(f"{BASE_URL}/courses/{course_id}/buy/", headers=headers)
    print(f"Status: {r.status_code}")
    try:
        pay_url = r.json().get('pay_url')
        print(f"Pay URL: {pay_url}")
    except Exception as e:
        print(f"JSON Error: {e}")
        print(f"Response Text: {r.text[:2000]}")
        return
    
    if not pay_url:
        print("Failed to get pay url")
        return
        
    order_id = pay_url.split('=')[-1]
    print(f"Order ID: {order_id}")

    
    print(f"\n--- 7. Payment Webhook (Success) ---")
    webhook_data = {
        "order_id": order_id,
        "status": "success"
    }
    r = session.post(f"{BASE_URL}/payment-webhook", json=webhook_data)
    print(f"Status: {r.status_code} (Expected 204)")

    
    print(f"\n--- 8. My Orders ---")
    r = session.get(f"{BASE_URL}/orders", headers=headers)
    try:
        orders = r.json().get('data', [])
        print(f"Found {len(orders)} orders.")
        if orders:
            print(f"Order status: {orders[0]['payment_status']} (Expected 'success')")
    except Exception as e:
        print(f"JSON Error: {e}")
        print(f"Response Text: {r.text[:2000]}")
        return

    
    print(f"\n--- 9. Admin Certificate Generation (Internal) ---")
    
    enrollment = Enrollment.objects.get(order_id=order_id)
    print(f"Enrollment Status in DB: {enrollment.status}")
    
    if enrollment.status == 'success':
        
        
        
         происходит на стороне сервера."
        
        
        
        
        
        
        valid_cert = "123456123451" 
        invalid_cert = "123456123452" 
        
        print("\n--- 10. Check Certificate API ---")
        r = session.post(f"{BASE_URL}/check-sertificate", json={"sertikate_number": valid_cert})
        print(f"Valid Cert Check: {r.json()} (Expected success)")
        
        r = session.post(f"{BASE_URL}/check-sertificate", json={"sertikate_number": invalid_cert})
        print(f"Invalid Cert Check: {r.json()} (Expected failed)")

if __name__ == "__main__":
    cid = create_test_data()
    test_flow(cid)
