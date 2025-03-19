import os
import django
from django.utils import timezone
from datetime import date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from accounts.models import CustomUser, Department

def create_dummy_users():
    # Create Computer Science department if it doesn't exist
    cs_dept, created = Department.objects.get_or_create(name='Computer Science')
    if created:
        print(f"Created department: {cs_dept.name}")
    
    # Create staff users
    staff_users = [
        {
            'username': 'professor1',
            'password': 'staff123',
            'email': 'professor1@college.edu',
            'first_name': 'John',
            'last_name': 'Smith',
            'user_type': 'staff',
            'department': cs_dept,
            'staff_id': 'CS001',
            'designation': 'Professor',
            'phone_number': '1234567890',
            'date_of_joining': date(2020, 1, 1),
            'qualification': 'Ph.D.',
            'specialization': 'Machine Learning',
            'office_location': 'Room 101, CS Building'
        },
        {
            'username': 'professor2',
            'password': 'staff123',
            'email': 'professor2@college.edu',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'user_type': 'staff',
            'department': cs_dept,
            'staff_id': 'CS002',
            'designation': 'Associate Professor',
            'phone_number': '1234567891',
            'date_of_joining': date(2021, 1, 1),
            'qualification': 'Ph.D.',
            'specialization': 'Data Science',
            'office_location': 'Room 102, CS Building'
        }
    ]

    # Create student users
    student_users = [
        {
            'username': 'student1',
            'password': 'student123',
            'email': 'student1@college.edu',
            'first_name': 'Alex',
            'last_name': 'Brown',
            'user_type': 'student',
            'department': cs_dept,
            'student_id': 'CS2024001',
            'semester': 1,
            'section': 'A',
            'roll_number': 'CS001',
            'batch_year': 2024,
            'phone_number': '9876543210',
            'date_of_birth': date(2000, 1, 1),
            'address': '123 Student Street',
            'blood_group': 'A+',
            'emergency_contact': '9876543211',
            'parent_name': 'Robert Brown',
            'parent_phone': '9876543212'
        },
        {
            'username': 'student2',
            'password': 'student123',
            'email': 'student2@college.edu',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'user_type': 'student',
            'department': cs_dept,
            'student_id': 'CS2024002',
            'semester': 1,
            'section': 'B',
            'roll_number': 'CS002',
            'batch_year': 2024,
            'phone_number': '9876543213',
            'date_of_birth': date(2000, 2, 1),
            'address': '456 Student Avenue',
            'blood_group': 'B+',
            'emergency_contact': '9876543214',
            'parent_name': 'Mary Wilson',
            'parent_phone': '9876543215'
        },
        {
            'username': 'student3',
            'password': 'student123',
            'email': 'student3@college.edu',
            'first_name': 'Michael',
            'last_name': 'Davis',
            'user_type': 'student',
            'department': cs_dept,
            'student_id': 'CS2024003',
            'semester': 2,
            'section': 'A',
            'roll_number': 'CS003',
            'batch_year': 2023,
            'phone_number': '9876543216',
            'date_of_birth': date(1999, 3, 1),
            'address': '789 Student Road',
            'blood_group': 'O+',
            'emergency_contact': '9876543217',
            'parent_name': 'David Davis',
            'parent_phone': '9876543218'
        }
    ]

    # Create staff users
    for staff_data in staff_users:
        user, created = CustomUser.objects.get_or_create(
            username=staff_data['username'],
            defaults={
                'email': staff_data['email'],
                'first_name': staff_data['first_name'],
                'last_name': staff_data['last_name'],
                'user_type': staff_data['user_type'],
                'department': staff_data['department'],
                'staff_id': staff_data['staff_id'],
                'designation': staff_data['designation'],
                'phone_number': staff_data['phone_number'],
                'date_of_joining': staff_data['date_of_joining'],
                'qualification': staff_data['qualification'],
                'specialization': staff_data['specialization'],
                'office_location': staff_data['office_location']
            }
        )
        if created:
            user.set_password(staff_data['password'])
            user.save()
            print(f"Created staff user: {user.username}")
            print(f"Username: {user.username}")
            print(f"Password: {staff_data['password']}")
        else:
            print(f"Staff user already exists: {user.username}")
            print(f"Username: {user.username}")
            print(f"Password: {staff_data['password']}")

    # Create student users
    for student_data in student_users:
        user, created = CustomUser.objects.get_or_create(
            username=student_data['username'],
            defaults={
                'email': student_data['email'],
                'first_name': student_data['first_name'],
                'last_name': student_data['last_name'],
                'user_type': student_data['user_type'],
                'department': student_data['department'],
                'student_id': student_data['student_id'],
                'semester': student_data['semester'],
                'section': student_data['section'],
                'roll_number': student_data['roll_number'],
                'batch_year': student_data['batch_year'],
                'phone_number': student_data['phone_number'],
                'date_of_birth': student_data['date_of_birth'],
                'address': student_data['address'],
                'blood_group': student_data['blood_group'],
                'emergency_contact': student_data['emergency_contact'],
                'parent_name': student_data['parent_name'],
                'parent_phone': student_data['parent_phone']
            }
        )
        if created:
            user.set_password(student_data['password'])
            user.save()
            print(f"Created student user: {user.username}")
            print(f"Username: {user.username}")
            print(f"Password: {student_data['password']}")
        else:
            print(f"Student user already exists: {user.username}")
            print(f"Username: {user.username}")
            print(f"Password: {student_data['password']}")

if __name__ == '__main__':
    create_dummy_users() 