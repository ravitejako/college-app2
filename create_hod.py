import os
import django
from django.conf import settings
from datetime import date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from accounts.models import CustomUser, Department

def create_hod():
    # Get the Computer Science department
    cs_dept = Department.objects.get(name='Computer Science')
    
    # Create HOD user
    hod_user, created = CustomUser.objects.get_or_create(
        username='hod_cs',
        defaults={
            'email': 'hod.cs@college.edu',
            'first_name': 'Dr. Robert',
            'last_name': 'Wilson',
            'user_type': 'hod',
            'department': cs_dept,
            'staff_id': 'CSHOD001',
            'designation': 'Professor & HOD',
            'phone_number': '1234567899',
            'date_of_joining': date(2015, 1, 1),
            'qualification': 'Ph.D.',
            'specialization': 'Computer Science',
            'office_location': 'Room 201, CS Building',
            'is_department_head': True,
            'department_managed': cs_dept
        }
    )
    
    if created:
        hod_user.set_password('hod123')
        hod_user.save()
        print(f"Created HOD user: {hod_user.username}")
    else:
        print(f"HOD user already exists: {hod_user.username}")

if __name__ == '__main__':
    create_hod() 