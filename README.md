# College Attendance Management System

A Django-based web application for managing student attendance in a college setting. This system allows staff members to take attendance and students to view their attendance records.

## Features

- Staff can take attendance for their classes
- Students can view their attendance records
- User authentication for both staff and students
- Secure access control based on user roles
- Dark/Light theme toggle with auto-detection
- Responsive design for mobile and desktop

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Access the application at http://127.0.0.1:8000/

## User Roles

- **Staff**: Can take attendance and view attendance records
- **Students**: Can view their own attendance records
- **Admin**: Full access to manage users and system settings 
- **HOD (Head of Department)**: Can manage staff, subjects, and department settings
