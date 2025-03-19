import os
import django
import datetime
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from accounts.models import CustomUser
from attendance.models import Department, Subject, Class

# Get the Computer Science department
cs_dept = Department.objects.get(name="Computer Science")
print(f"Found Computer Science department")

# Get or create staff members if needed
staff_user = CustomUser.objects.filter(user_type='staff').first()
if not staff_user:
    print("No staff user found. Creating a default staff user...")
    staff_user = CustomUser.objects.create_user(
        username="staff_user",
        email="staff@example.com",
        password="password123",
        first_name="Staff",
        last_name="User",
        user_type='staff',
        staff_id="STAFF001"
    )
    print(f"Created staff user: {staff_user.username}")
else:
    print(f"Using existing staff user: {staff_user.username}")

# Create subjects if none exist
subjects = Subject.objects.filter(department=cs_dept)
if not subjects.exists():
    print("No subjects found. Creating dummy subjects...")
    
    # Create subjects for each semester
    subject_data = [
        # Semester 1
        {"name": "Introduction to Programming", "code": "CS101", "semester": 1},
        {"name": "Computer Fundamentals", "code": "CS102", "semester": 1},
        {"name": "Mathematics for Computing", "code": "CS103", "semester": 1},
        
        # Semester 2
        {"name": "Data Structures", "code": "CS201", "semester": 2},
        {"name": "Object-Oriented Programming", "code": "CS202", "semester": 2},
        {"name": "Database Systems", "code": "CS203", "semester": 2},
        
        # Semester 3
        {"name": "Algorithms", "code": "CS301", "semester": 3},
        {"name": "Web Development", "code": "CS302", "semester": 3},
        {"name": "Operating Systems", "code": "CS303", "semester": 3},
    ]
    
    for data in subject_data:
        subject = Subject.objects.create(
            name=data["name"],
            code=data["code"],
            semester=data["semester"],
            department=cs_dept,
            staff=staff_user,
            credits=4
        )
        print(f"Created subject: {subject.name} (Semester {subject.semester})")
    
    # Refresh subjects queryset
    subjects = Subject.objects.filter(department=cs_dept)

print(f"Found {subjects.count()} subjects")

# Create classes for each subject
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)
day_after = today + datetime.timedelta(days=2)

# List of dates to create classes for
dates = [yesterday, today, tomorrow, day_after]

# Time slots for classes
time_slots = [
    (datetime.time(9, 0), datetime.time(10, 30)),
    (datetime.time(11, 0), datetime.time(12, 30)),
    (datetime.time(14, 0), datetime.time(15, 30)),
    (datetime.time(16, 0), datetime.time(17, 30))
]

# Create classes for each subject on each date
for subject in subjects:
    for date in dates:
        # Pick a random time slot for this subject on this date
        time_slot = random.choice(time_slots)
        
        # Check if class already exists
        if Class.objects.filter(subject=subject, date=date).exists():
            print(f"Class for {subject.name} on {date} already exists")
            continue
            
        class_obj = Class.objects.create(
            subject=subject,
            date=date,
            start_time=time_slot[0],
            end_time=time_slot[1]
        )
        print(f"Created class for {subject.name} on {date} from {time_slot[0]} to {time_slot[1]}")

print("Dummy classes created successfully!")
print("Now run create_dummy_students.py to create students and attendance records.") 