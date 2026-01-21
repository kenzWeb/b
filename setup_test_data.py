import os
import django
import sys
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course

def create_future_course():
    # Check if exists first to avoid dupes
    if Course.objects.filter(name="Future Course 2027").exists():
        print("Future Course 2027 already exists.")
        return

    future_date = datetime.date.today() + datetime.timedelta(days=365)
    c = Course.objects.create(
        name="Future Course 2027",
        description="Auto-generated for verification",
        hours=10,
        price=5000,
        start_date=future_date,
        end_date=future_date + datetime.timedelta(days=30)
    )
    print(f"Created course: {c.name} (ID: {c.id})")

if __name__ == "__main__":
    create_future_course()
