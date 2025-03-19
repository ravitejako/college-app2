from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from attendance.models import Department, Subject, Class, Attendance, LeaveRequest
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Creates initial data for the attendance system'

    def handle(self, *args, **kwargs):
        # Create Department
        cs_dept, created = Department.objects.get_or_create(
            name='Computer Science',
            code='CS'
        )
        self.stdout.write(self.style.SUCCESS(f"Department {'created' if created else 'already exists'}: {cs_dept}"))

        # Create Staff User
        staff_user, created = CustomUser.objects.get_or_create(
            username='staff1',
            email='staff1@example.com',
            first_name='John',
            last_name='Doe'
        )
        if created:
            staff_user.set_password('staff123')
            staff_user.save()
            self.stdout.write(self.style.SUCCESS(f"Staff user created: {staff_user}"))

        # Create Subject
        subject, created = Subject.objects.get_or_create(
            name='Python Programming',
            code='CS101',
            department=cs_dept,
            staff=staff_user,
            semester=1,
            credits=3
        )
        self.stdout.write(self.style.SUCCESS(f"Subject {'created' if created else 'already exists'}: {subject}"))

        # Create Class Schedule
        class_schedule, created = Class.objects.get_or_create(
            subject=subject,
            date=timezone.now().date(),
            start_time='09:00',
            end_time='10:00',
            room_number='Room 101',
            topic='Introduction to Python'
        )
        self.stdout.write(self.style.SUCCESS(f"Class schedule {'created' if created else 'already exists'}: {class_schedule}"))

        # Create Student User
        student_user, created = CustomUser.objects.get_or_create(
            username='student1',
            email='student1@example.com',
            first_name='Jane',
            last_name='Smith'
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
            self.stdout.write(self.style.SUCCESS(f"Student user created: {student_user}"))

        # Create Attendance Record
        attendance, created = Attendance.objects.get_or_create(
            student=student_user,
            class_session=class_schedule,
            is_present=True,
            marked_by=staff_user
        )
        self.stdout.write(self.style.SUCCESS(f"Attendance record {'created' if created else 'already exists'}: {attendance}"))

        # Create Leave Request
        leave_request, created = LeaveRequest.objects.get_or_create(
            student=student_user,
            subject=subject,
            leave_type='sick',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=1),
            reason='Doctor appointment'
        )
        self.stdout.write(self.style.SUCCESS(f"Leave request {'created' if created else 'already exists'}: {leave_request}")) 