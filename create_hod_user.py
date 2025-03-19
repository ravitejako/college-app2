import os
import django
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from accounts.models import CustomUser, Department as AccountsDepartment
from attendance.models import Department

# Get or create the Computer Science department in accounts app
accounts_cs_dept, created = AccountsDepartment.objects.get_or_create(
    name="Computer Science",
    defaults={
        'code': 'CS',
        'description': 'Department of Computer Science'
    }
)
print(f"Accounts Computer Science department {'created' if created else 'already exists'}")

# Check if HOD user already exists
hod_username = "cs_hod"
if CustomUser.objects.filter(username=hod_username).exists():
    print(f"HOD user {hod_username} already exists")
    hod_user = CustomUser.objects.get(username=hod_username)
else:
    # Create HOD user
    hod_user = CustomUser.objects.create_user(
        username=hod_username,
        email="hod@example.com",
        password="password123",
        first_name="Department",
        last_name="Head",
        user_type='hod',
        department=accounts_cs_dept,
        staff_id="HOD001",
        designation="Head of Department",
        date_of_joining=datetime.date(2020, 1, 1),
        qualification="Ph.D. in Computer Science",
        specialization="Computer Science",
        office_location="CS Building, Room 101",
        phone_number="555-HOD-1234"
    )
    print(f"Created HOD user: {hod_user.username}")

print("\nHOD User Details:")
print(f"Username: {hod_user.username}")
print(f"Password: password123")
print(f"Name: {hod_user.get_full_name()}")
print(f"Department: {hod_user.department.name if hod_user.department else 'None'}")
print(f"User Type: {hod_user.user_type}")

print("\nYou can now log in as HOD with the following credentials:")
print("Username: cs_hod")
print("Password: password123") 