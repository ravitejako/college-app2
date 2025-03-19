import os
import django
import datetime
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from accounts.models import CustomUser, Department as AccountsDepartment
from attendance.models import Department, Subject, Class

# Get the Computer Science department from attendance app
cs_dept, created = Department.objects.get_or_create(
    name="Computer Science",
    defaults={
        'code': 'CS'
    }
)
print(f"Computer Science department {'created' if created else 'already exists'}")

# Get or create the Computer Science department in accounts app for students
accounts_cs_dept, created = AccountsDepartment.objects.get_or_create(
    name="Computer Science",
    defaults={
        'code': 'CS',
        'description': 'Department of Computer Science'
    }
)
print(f"Accounts Computer Science department {'created' if created else 'already exists'}")

# Get existing subjects
subjects = Subject.objects.filter(department=cs_dept)
if not subjects.exists():
    print("No subjects found. Please run create_dummy_data.py first.")
    exit(1)

print(f"Found {subjects.count()} subjects")

# Create 5 dummy students for each semester (1-3)
for semester in range(1, 4):
    for i in range(1, 6):
        username = f"student_s{semester}_{i}"
        email = f"student{semester}_{i}@example.com"
        
        # Check if student already exists
        if CustomUser.objects.filter(username=username).exists():
            print(f"Student {username} already exists")
            continue
            
        student = CustomUser.objects.create_user(
            username=username,
            email=email,
            password="password123",
            first_name=f"Student{i}",
            last_name=f"Semester{semester}",
            user_type='student',
            department=accounts_cs_dept,
            semester=semester,
            student_id=f"STU{semester}{i}",
            date_of_birth=datetime.date(2000, random.randint(1, 12), random.randint(1, 28)),
            phone_number=f"555-{semester}{i}{i}{i}-{i}{i}{i}{i}"
        )
        print(f"Created student: {student.username} (Semester {semester})")

# Create attendance records for each class
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# Get all classes for today and yesterday
classes = Class.objects.filter(date__in=[today, yesterday])
students = CustomUser.objects.filter(user_type='student')

print(f"Found {classes.count()} classes and {students.count()} students")

# Create attendance records
from attendance.models import Attendance

for class_obj in classes:
    # Get students for this class's subject semester
    semester_students = students.filter(semester=class_obj.subject.semester)
    
    for student in semester_students:
        # Randomly mark students as present (80% chance) or absent
        is_present = random.random() < 0.8
        
        # Check if attendance record already exists
        attendance, created = Attendance.objects.get_or_create(
            class_session=class_obj,
            student=student,
            defaults={
                'is_present': is_present,
                'marked_by': class_obj.subject.staff
            }
        )
        
        if created:
            status = "present" if is_present else "absent"
            print(f"Marked {student.username} as {status} for {class_obj.subject.name} on {class_obj.date}")
        else:
            print(f"Attendance record already exists for {student.username} in {class_obj.subject.name} on {class_obj.date}")

print("Dummy students and attendance records created successfully!") 