import os
import django
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_attendance.settings')
django.setup()

from accounts.models import CustomUser
from attendance.models import Class, Subject, Department

# Create Computer Science department if it doesn't exist
cs_dept, created = Department.objects.get_or_create(
    name="Computer Science",
    defaults={
        'code': 'CS'
    }
)
print(f"Computer Science department {'created' if created else 'already exists'}")

# Get the HOD user
try:
    hod_user = CustomUser.objects.get(username='hod_cs')
    print(f"Found HOD user: {hod_user.username}")
except CustomUser.DoesNotExist:
    print("HOD user not found")

# Get a staff user for the subjects
try:
    staff_user = CustomUser.objects.filter(user_type='staff').first()
    if not staff_user:
        print("No staff user found. Please create a staff user first.")
    else:
        print(f"Using staff user: {staff_user.username}")
        
        # Create dummy subjects
        subjects_data = [
            {
                'code': 'CS101',
                'name': 'Introduction to Programming',
                'department': cs_dept,
                'staff': staff_user,
                'semester': 1,
                'credits': 4,
                'total_classes': 30
            },
            {
                'code': 'CS201',
                'name': 'Data Structures',
                'department': cs_dept,
                'staff': staff_user,
                'semester': 2,
                'credits': 4,
                'total_classes': 30
            },
            {
                'code': 'CS301',
                'name': 'Database Systems',
                'department': cs_dept,
                'staff': staff_user,
                'semester': 3,
                'credits': 3,
                'total_classes': 25
            }
        ]
        
        # Create subjects
        created_subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'department': subject_data['department'],
                    'staff': subject_data['staff'],
                    'semester': subject_data['semester'],
                    'credits': subject_data['credits'],
                    'total_classes': subject_data['total_classes']
                }
            )
            status = 'created' if created else 'already exists'
            print(f"Subject {subject.code}: {subject.name} {status}")
            created_subjects.append(subject)
        
        # Create classes for today and yesterday
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        try:
            # Get the subjects from the database to ensure we have proper instances
            subject_codes = [s.code for s in created_subjects]
            db_subjects = Subject.objects.filter(code__in=subject_codes)
            
            for subject in db_subjects:
                # Create a class for today
                today_class, created = Class.objects.get_or_create(
                    subject=subject,
                    date=today,
                    defaults={
                        'start_time': datetime.time(9, 0),  # 9:00 AM
                        'end_time': datetime.time(10, 30),  # 10:30 AM
                        'room_number': f'Room-{subject.code}',
                        'topic': f'Topic for {subject.name}',
                        'notes': f'Notes for {subject.name} class'
                    }
                )
                print(f"Class for {subject.code} on {today}: {'created' if created else 'already exists'}")
                
                # Create a class for yesterday
                yesterday_class, created = Class.objects.get_or_create(
                    subject=subject,
                    date=yesterday,
                    defaults={
                        'start_time': datetime.time(14, 0),  # 2:00 PM
                        'end_time': datetime.time(15, 30),  # 3:30 PM
                        'room_number': f'Room-{subject.code}',
                        'topic': f'Previous topic for {subject.name}',
                        'notes': f'Previous notes for {subject.name} class'
                    }
                )
                print(f"Class for {subject.code} on {yesterday}: {'created' if created else 'already exists'}")
        except Exception as e:
            print(f"Error creating classes: {str(e)}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"Error: {str(e)}")

print("Dummy data creation completed!") 