import os
import django
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from attendance.models import Department, Subject, Staff, Student, ClassSchedule, LeaveRequest

def create_initial_data():
    # Create Department
    cs_dept, created = Department.objects.get_or_create(
        name='Computer Science',
        code='CS'
    )
    print(f"Department {'created' if created else 'already exists'}: {cs_dept}")

    # Create Staff User
    staff_user, created = User.objects.get_or_create(
        username='staff1',
        email='staff1@example.com',
        first_name='John',
        last_name='Doe'
    )
    if created:
        staff_user.set_password('staff123')
        staff_user.save()
        print(f"Staff user created: {staff_user}")

    # Create Staff Profile
    staff, created = Staff.objects.get_or_create(
        user=staff_user,
        department=cs_dept,
        designation='Assistant Professor',
        phone='1234567890'
    )
    print(f"Staff profile {'created' if created else 'already exists'}: {staff}")

    # Create Subject
    subject, created = Subject.objects.get_or_create(
        name='Python Programming',
        code='CS101',
        department=cs_dept
    )
    print(f"Subject {'created' if created else 'already exists'}: {subject}")

    # Create Class Schedule
    schedule, created = ClassSchedule.objects.get_or_create(
        subject=subject,
        staff=staff,
        room='Room 101',
        day='Monday',
        start_time='09:00',
        end_time='10:00',
        semester=1
    )
    print(f"Class schedule {'created' if created else 'already exists'}: {schedule}")

    # Create Student User
    student_user, created = User.objects.get_or_create(
        username='student1',
        email='student1@example.com',
        first_name='Jane',
        last_name='Smith'
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
        print(f"Student user created: {student_user}")

    # Create Student Profile
    student, created = Student.objects.get_or_create(
        user=student_user,
        department=cs_dept,
        roll_number='CS001',
        semester=1
    )
    print(f"Student profile {'created' if created else 'already exists'}: {student}")

if __name__ == '__main__':
    create_initial_data() 