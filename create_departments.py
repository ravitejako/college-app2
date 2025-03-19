import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from accounts.models import Department

def create_departments():
    # Create Computer Science department
    cs_dept, created = Department.objects.get_or_create(
        name='Computer Science',
        code='CS',
        defaults={
            'description': 'Department of Computer Science'
        }
    )
    print(f"Department {'created' if created else 'already exists'}: {cs_dept}")
    return cs_dept

if __name__ == '__main__':
    create_departments() 