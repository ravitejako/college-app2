from django.core.management.base import BaseCommand
from accounts.models import Department

class Command(BaseCommand):
    help = 'Creates default departments'

    def handle(self, *args, **kwargs):
        departments = [
            {'name': 'Computer Science', 'code': 'CS'},
            {'name': 'Information Technology', 'code': 'IT'},
            {'name': 'Electronics', 'code': 'ECE'},
            {'name': 'Mechanical', 'code': 'MECH'},
            {'name': 'Civil', 'code': 'CIVIL'},
            {'name': 'Electrical', 'code': 'EEE'},
            {'name': 'Physics', 'code': 'PHY'},
            {'name': 'Chemistry', 'code': 'CHEM'},
            {'name': 'Mathematics', 'code': 'MATH'},
            {'name': 'English', 'code': 'ENG'},
            {'name': 'Management', 'code': 'MGT'},
            {'name': 'Commerce', 'code': 'COM'},
            {'name': 'Arts', 'code': 'ARTS'}
        ]

        for dept in departments:
            Department.objects.get_or_create(
                name=dept['name'],
                code=dept['code']
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created department {dept["name"]}')
            ) 