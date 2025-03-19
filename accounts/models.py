from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @classmethod
    def get_default_pk(cls):
        dept, created = cls.objects.get_or_create(
            name='General',
            defaults={'code': 'GEN', 'description': 'Default department for users'}
        )
        return dept.pk

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('hod', 'HOD'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
    )

    QUALIFICATION_CHOICES = (
        ('phd', 'Ph.D.'),
        ('masters', "Master's Degree"),
        ('bachelors', "Bachelor's Degree"),
        ('other', 'Other'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    
    # Student specific fields
    student_id = models.CharField(max_length=20, blank=True, null=True)
    semester = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    batch_year = models.IntegerField(null=True, blank=True)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Staff specific fields
    staff_id = models.CharField(max_length=20, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    date_of_joining = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    
    # HOD specific fields
    is_department_head = models.BooleanField(default=False)
    department_managed = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_head')
    
    # Professional profile fields
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated list of skills")
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'staff'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

# Renamed from Attendance to UserAttendance to avoid conflicts
class UserAttendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_attendances', limit_choices_to={'user_type': 'student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='marked_user_attendances', limit_choices_to={'user_type': 'staff'})
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject', 'date']
        ordering = ['-date', 'student']

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student} - {self.subject} - {self.date} - {status}"

class Result(models.Model):
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    grade = models.CharField(max_length=2)
    exam_type = models.CharField(max_length=50, choices=[
        ('internal_1', 'Internal 1'),
        ('internal_2', 'Internal 2'),
        ('semester_end', 'Semester End Exam'),
    ])
    date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date', 'subject']
    
    def save(self, *args, **kwargs):
        # Calculate grade based on marks
        percentage = (self.marks_obtained / self.max_marks) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C'
        elif percentage >= 40:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} ({self.exam_type})"

class Experience(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.position} at {self.organization}"
    
    class Meta:
        ordering = ['-start_date']

class Education(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.degree} from {self.institution}"
    
    class Meta:
        ordering = ['-end_year']
        verbose_name_plural = "Education"

class Publication(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=200)
    journal = models.CharField(max_length=100)
    year = models.IntegerField()
    url = models.URLField(blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-year']

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    file_attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-due_date']

class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late Submission'),
        ('resubmit', 'Needs Resubmission'),
    )
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignment_submissions')
    submission_date = models.DateTimeField(auto_now_add=True)
    submission_file = models.FileField(upload_to='assignment_submissions/', null=True, blank=True)
    submission_text = models.TextField(blank=True)
    marks = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}"
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submission_date']
