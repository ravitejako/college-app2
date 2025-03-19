from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import datetime, timedelta
from calendar import month_name
from .forms import StudentRegistrationForm, StaffRegistrationForm, CollegeRegistrationForm, CustomAuthenticationForm, ProfessionalProfileForm, ExperienceForm, EducationForm, PublicationForm, AssignmentForm, AssignmentGradingForm, AssignmentSubmissionForm
from .models import CustomUser, Subject, UserAttendance, Result, Assignment, AssignmentSubmission
from attendance.models import Attendance, Class, Department
from urllib.parse import urlencode

# Create your views here.

class StudentRegistrationView(CreateView):
    form_class = StudentRegistrationForm
    template_name = 'accounts/student_register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # First save the user instance
        user = form.save(commit=False)
        user.user_type = 'student'
        
        # Save all the basic user fields
        user.username = form.cleaned_data.get('username')
        user.email = form.cleaned_data.get('email')
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.set_password(form.cleaned_data.get('password1'))
        
        # Save student specific fields
        user.department = form.cleaned_data.get('department')
        user.student_id = form.cleaned_data.get('student_id')
        user.semester = form.cleaned_data.get('semester')
        user.phone_number = form.cleaned_data.get('phone_number')
        user.date_of_birth = form.cleaned_data.get('date_of_birth')
        user.address = form.cleaned_data.get('address')
        user.blood_group = form.cleaned_data.get('blood_group')
        user.emergency_contact = form.cleaned_data.get('emergency_contact')
        user.parent_name = form.cleaned_data.get('parent_name')
        user.parent_phone = form.cleaned_data.get('parent_phone')
        
        # Handle profile picture if provided
        profile_picture = form.cleaned_data.get('profile_picture')
        if profile_picture:
            user.profile_picture = profile_picture
        
        # Save the user instance
        user.save()
        
        messages.success(self.request, 'Registration successful! Please log in with your credentials.')
        return super().form_valid(form)

class StaffRegistrationView(CreateView):
    form_class = StaffRegistrationForm
    template_name = 'accounts/staff_register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # First save the user instance
        user = form.save(commit=False)
        user.user_type = 'staff'
        
        # Save all the basic user fields
        user.username = form.cleaned_data.get('username')
        user.email = form.cleaned_data.get('email')
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.set_password(form.cleaned_data.get('password1'))
        
        # Save staff specific fields
        user.department = form.cleaned_data.get('department')
        user.staff_id = form.cleaned_data.get('staff_id')
        user.designation = form.cleaned_data.get('designation')
        user.phone_number = form.cleaned_data.get('phone_number')
        user.date_of_joining = form.cleaned_data.get('date_of_joining')
        user.qualification = form.cleaned_data.get('qualification')
        user.specialization = form.cleaned_data.get('specialization')
        user.office_location = form.cleaned_data.get('office_location')
        
        # Handle profile picture if provided
        profile_picture = form.cleaned_data.get('profile_picture')
        if profile_picture:
            user.profile_picture = profile_picture
        
        # Save the user instance
        user.save()
        
        messages.success(self.request, 'Registration successful! Please log in with your credentials.')
        return super().form_valid(form)

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    user = request.user
    today = timezone.now().date()
    
    # Get attendance records for the current student
    attendance_records = Attendance.objects.filter(
        student=user
    ).select_related('class_session', 'class_session__subject')
    
    # Calculate overall attendance
    total_classes = attendance_records.count()
    classes_present = attendance_records.filter(is_present=True).count()
    attendance_percentage = (classes_present / total_classes * 100) if total_classes > 0 else 0
    
    # Get attendance by subject
    subjects = Subject.objects.filter(classes__attendances__student=user).distinct()
    subject_attendance = []
    chart_data = []
    chart_labels = []
    
    for subject in subjects:
        subject_records = attendance_records.filter(class_session__subject_id=subject.id)
        total = subject_records.count()
        present = subject_records.filter(is_present=True).count()
        if total > 0:
            percentage = round((present / total * 100), 1)
            subject_attendance.append({
                'name': subject.name,
                'code': subject.code,
                'total': total,
                'present': present,
                'percentage': percentage
            })
            chart_data.append(percentage)
            chart_labels.append(f'"{subject.name}"')
    
    context = {
        'attendance_percentage': round(attendance_percentage, 1),
        'total_classes': total_classes,
        'classes_present': classes_present,
        'classes_absent': total_classes - classes_present,
        'subject_attendance': subject_attendance,
        'chart_data': chart_data,
        'chart_labels': chart_labels,
    }
    
    return render(request, 'accounts/student_dashboard.html', context)

@login_required
def staff_dashboard(request):
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    user = request.user
    today = timezone.now().date()
    
    # Get all subjects taught by the staff member
    subjects = Subject.objects.filter(staff=user)
    
    # Get all classes and their attendance for today
    todays_classes = Class.objects.filter(
        subject__staff=user,
        date=today
    ).select_related('subject')
    
    # Calculate attendance statistics
    attendance_stats = []
    chart_data = []
    chart_labels = []
    
    for subject in subjects:
        # Get all attendance records for this subject
        # Use the subject ID instead of the subject object
        class_sessions = Class.objects.filter(subject_id=subject.id)
        total_students = CustomUser.objects.filter(user_type='student').count()
        total_attendance = Attendance.objects.filter(class_session__subject_id=subject.id)
        present_count = total_attendance.filter(is_present=True).count()
        total_count = total_attendance.count()
        
        if total_count > 0:
            attendance_percentage = round((present_count / total_count * 100), 1)
        else:
            attendance_percentage = 0
        
        attendance_stats.append({
            'subject': subject.name,
            'code': subject.code,
            'total_classes': class_sessions.count(),
            'total_students': total_students,
            'attendance_percentage': attendance_percentage
        })
        
        chart_labels.append(f'"{subject.name}"')
        chart_data.append(attendance_percentage)
    
    # Get recent attendance records
    recent_attendance = Attendance.objects.filter(
        class_session__subject__staff=user
    ).select_related(
        'student', 'class_session', 'class_session__subject'
    ).order_by('-class_session__date')[:10]
    
    context = {
        'today_date': today.strftime('%B %d, %Y'),
        'subjects_count': subjects.count(),
        'todays_classes': todays_classes,
        'attendance_stats': attendance_stats,
        'recent_attendance': recent_attendance,
        'chart_data': chart_data,
        'chart_labels': chart_labels,
    }
    
    return render(request, 'accounts/staff_dashboard.html', context)

@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
        'page_title': f'Profile - {user.get_full_name()}',
    }
    return render(request, 'accounts/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = CollegeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Welcome to the system.')
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CollegeRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def menu(request):
    return render(request, 'accounts/menu.html')

def index(request):
    """Landing page view redirecting to login."""
    return redirect('login')

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    return render(request, 'accounts/logout.html')

def login_view(request):
    role = request.GET.get('role', '')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user type matches the role
                if role == 'staff' and user.user_type != 'staff':
                    messages.error(request, 'Access denied. This login is for staff only.')
                    return redirect('login')
                elif role == 'student' and user.user_type != 'student':
                    messages.error(request, 'Access denied. This login is for students only.')
                    return redirect('login')
                elif role == 'hod' and user.user_type != 'hod':
                    messages.error(request, 'Access denied. This login is for HOD only.')
                    return redirect('login')
                else:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    if user.user_type == 'staff':
                        return redirect('staff_dashboard')
                    elif user.user_type == 'hod':
                        return redirect('hod_dashboard')
                    else:
                        return redirect('profile')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'role': role
    })

@login_required
def student_fee(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    context = {
        'user': user,
    }
    return render(request, 'accounts/student_fee.html', context)

@login_required
def student_results(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    context = {
        'user': user,
    }
    return render(request, 'accounts/student_results.html', context)

@login_required
def enrollment(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    context = {
        'user': user,
        'page_title': 'Enrollment'
    }
    return render(request, 'accounts/enrollment.html', context)

@login_required
def semester_enrollment(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    context = {
        'user': user,
        'page_title': 'Semester Enrollment'
    }
    return render(request, 'accounts/semester_enrollment.html', context)

@login_required
def activity(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    context = {
        'user': user,
        'page_title': 'Activity'
    }
    return render(request, 'accounts/activity.html', context)

@login_required
def feedback(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    context = {
        'user': user,
        'page_title': 'Feedback'
    }
    return render(request, 'accounts/feedback.html', context)

@login_required
def announcement(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    context = {
        'user': user,
        'page_title': 'Announcements'
    }
    return render(request, 'accounts/announcement.html', context)

@login_required
def institution(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'My Institution'
    }
    return render(request, 'accounts/institution.html', context)

@login_required
def messages_view(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Messages'
    }
    return render(request, 'accounts/messages.html', context)

@login_required
def attendance(request):
    user = request.user
    
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    # Get filter parameters
    subject_id = request.GET.get('subject')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base query for attendance records
    attendance_records = Attendance.objects.filter(
        student=user
    ).select_related('class_session', 'class_session__subject').order_by('-class_session__date')
    
    # Apply filters if provided
    if subject_id:
        attendance_records = attendance_records.filter(class_session__subject_id=subject_id)
    
    if start_date:
        attendance_records = attendance_records.filter(class_session__date__gte=start_date)
    
    if end_date:
        attendance_records = attendance_records.filter(class_session__date__lte=end_date)
    
    # Calculate attendance statistics
    total_classes = attendance_records.count()
    classes_present = attendance_records.filter(is_present=True).count()
    classes_absent = total_classes - classes_present
    overall_percentage = round((classes_present / total_classes * 100) if total_classes > 0 else 0, 1)
    
    # Get all subjects for the filter dropdown - using the correct relationship path
    subjects = Subject.objects.filter(
        id__in=attendance_records.values_list('class_session__subject', flat=True)
    ).distinct()
    
    # Prepare chart data - attendance by subject
    chart_data = []
    chart_labels = []
    
    for subject in subjects:
        subject_attendance = attendance_records.filter(
            class_session__subject_id=subject.id
        )
        
        total = subject_attendance.count()
        present = subject_attendance.filter(is_present=True).count()
        
        if total > 0:
            percentage = round((present / total * 100), 1)
            chart_data.append(percentage)
            chart_labels.append(f'"{subject.name}"')  # Add quotes for JSON
    
    # Get current academic year and semester
    current_year = timezone.now().year
    academic_year = f"{current_year}-{current_year + 1}"
    current_semester = user.semester
    department = user.department.name if user.department else "Unknown"
    semester_display = f"{academic_year}, {current_semester}, {department}"
    
    context = {
        'user': user,
        'attendance_records': attendance_records,
        'total_classes': total_classes,
        'classes_present': classes_present,
        'classes_absent': classes_absent,
        'overall_percentage': overall_percentage,
        'subjects': subjects,
        'chart_data': chart_data,
        'chart_labels': chart_labels,
        'semester_display': semester_display,
        'current_filters': {
            'subject': subject_id,
            'start_date': start_date,
            'end_date': end_date,
        },
    }
    
    return render(request, 'accounts/attendance.html', context)

@login_required
def assignments(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    # Get assignments for the student's semester/subjects
    student_assignments = Assignment.objects.filter(subject__semester=user.semester)
    
    # Get the student's submissions
    submissions = {submission.assignment_id: submission for submission in 
                  AssignmentSubmission.objects.filter(student=user)}
    
    context = {
        'user': user,
        'assignments': student_assignments,
        'submissions': submissions,
        'now': timezone.now(),  # Add current time for comparing due dates
        'page_title': 'Assignments'
    }
    return render(request, 'accounts/assignments.html', context)

@login_required
def submit_assignment(request, assignment_id):
    """View for students to submit an assignment"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if the student has already submitted this assignment
    submission, created = AssignmentSubmission.objects.get_or_create(
        assignment=assignment,
        student=request.user
    )
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            # Check if submission is late
            if timezone.now() > assignment.due_date:
                submission.status = 'late'
            
            form.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignments')
    else:
        form = AssignmentSubmissionForm(instance=submission)
    
    context = {
        'form': form,
        'assignment': assignment,
        'submission': submission,
        'page_title': f'Submit Assignment: {assignment.title}'
    }
    return render(request, 'accounts/submit_assignment.html', context)

@login_required
def view_submission(request, submission_id):
    """View for students to view their submission and feedback"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, student=request.user)
    
    context = {
        'submission': submission,
        'assignment': submission.assignment,
        'page_title': f'Submission: {submission.assignment.title}'
    }
    return render(request, 'accounts/view_submission.html', context)

@login_required
def exam_schedules(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Exam Schedules'
    }
    return render(request, 'accounts/exam_schedules.html', context)

@login_required
def reports(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Reports'
    }
    return render(request, 'accounts/reports.html', context)

@login_required
def assessments(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Assessments'
    }
    return render(request, 'accounts/assessments.html', context)

@login_required
def holidays(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Holidays'
    }
    return render(request, 'accounts/holidays.html', context)

@login_required
def timetable(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Timetable'
    }
    return render(request, 'accounts/timetable.html', context)

@login_required
def teaching_content(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Teaching Content'
    }
    return render(request, 'accounts/teaching_content.html', context)

@login_required
def leave(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Leave'
    }
    return render(request, 'accounts/leave.html', context)

@login_required
def services(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Services'
    }
    return render(request, 'accounts/services.html', context)

@login_required
def billing(request):
    user = request.user
    if user.user_type != 'student':
        messages.error(request, 'Access denied. Student access only.')
        return redirect('login')
    context = {
        'user': user,
        'page_title': 'Billing'
    }
    return render(request, 'accounts/billing.html', context)

@login_required
def professional_profile(request, username=None):
    """
    Display a professional profile page for staff members.
    If username is provided, show that user's profile.
    Otherwise, show the logged-in user's profile.
    """
    if username:
        user = get_object_or_404(CustomUser, username=username, user_type='staff')
    else:
        user = request.user
        if user.user_type != 'staff':
            messages.error(request, 'Access denied. Staff access only.')
            return redirect('login')
    
    context = {
        'user': user,
        'page_title': f'Professional Profile - {user.get_full_name()}'
    }
    
    return render(request, 'accounts/professional_profile.html', context)

@login_required
def edit_professional_profile(request):
    """
    Allow staff members to edit their professional profile.
    """
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    if request.method == 'POST':
        form = ProfessionalProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your professional profile has been updated successfully.')
            return redirect('professional_profile')
    else:
        form = ProfessionalProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'page_title': 'Edit Professional Profile'
    }
    
    return render(request, 'accounts/edit_professional_profile.html', context)

@login_required
def add_experience(request):
    """
    Allow staff members to add professional experience.
    """
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.user = request.user
            experience.save()
            messages.success(request, 'Experience added successfully.')
            return redirect('profile')
    else:
        form = ExperienceForm()
    
    context = {
        'form': form,
        'page_title': 'Add Professional Experience'
    }
    
    return render(request, 'accounts/form_template.html', context)

@login_required
def add_education(request):
    """
    Allow staff members to add education details.
    """
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            messages.success(request, 'Education details added successfully.')
            return redirect('profile')
    else:
        form = EducationForm()
    
    context = {
        'form': form,
        'page_title': 'Add Education'
    }
    
    return render(request, 'accounts/form_template.html', context)

@login_required
def add_publication(request):
    """
    Allow staff members to add publications.
    """
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.user = request.user
            publication.save()
            messages.success(request, 'Publication added successfully.')
            return redirect('profile')
    else:
        form = PublicationForm()
    
    context = {
        'form': form,
        'page_title': 'Add Publication'
    }
    
    return render(request, 'accounts/form_template.html', context)

@login_required
def staff_assignments(request):
    """View for staff to manage their assignments"""
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    # Get assignments created by this staff member
    assignments = Assignment.objects.filter(created_by=request.user)
    
    context = {
        'assignments': assignments,
        'now': timezone.now(),  # Add current time for comparing due dates
        'page_title': 'Manage Assignments'
    }
    return render(request, 'accounts/staff_assignments.html', context)

@login_required
def create_assignment(request):
    """View for staff to create a new assignment"""
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('staff_assignments')
    else:
        form = AssignmentForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': 'Create Assignment'
    }
    return render(request, 'accounts/create_assignment.html', context)

@login_required
def edit_assignment(request, assignment_id):
    """View for staff to edit an existing assignment"""
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully!')
            return redirect('staff_assignments')
    else:
        form = AssignmentForm(instance=assignment, user=request.user)
    
    context = {
        'form': form,
        'assignment': assignment,
        'page_title': 'Edit Assignment'
    }
    return render(request, 'accounts/edit_assignment.html', context)

@login_required
def assignment_submissions(request, assignment_id):
    """View for staff to see all submissions for an assignment"""
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
        'page_title': f'Submissions: {assignment.title}'
    }
    return render(request, 'accounts/assignment_submissions.html', context)

@login_required
def grade_submission(request, submission_id):
    """View for staff to grade a student's submission"""
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment__created_by=request.user)
    
    if request.method == 'POST':
        form = AssignmentGradingForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Submission graded successfully!')
            return redirect('assignment_submissions', assignment_id=submission.assignment.id)
    else:
        form = AssignmentGradingForm(instance=submission)
    
    context = {
        'form': form,
        'submission': submission,
        'page_title': f'Grade Submission: {submission.student.get_full_name()}'
    }
    return render(request, 'accounts/grade_submission.html', context)

@login_required
def mark_attendance(request):
    """View for staff to mark attendance for a class"""
    if request.user.user_type != 'staff' and request.user.user_type != 'hod':
        messages.error(request, 'Access denied. Staff or HOD access only.')
        return redirect('login')
    
    # Import the correct models from the attendance app
    from attendance.models import Subject, Class, Attendance, Department
    
    # Get subjects taught by this staff member or all subjects for HOD
    if request.user.user_type == 'hod':
        # For HOD users, directly get the Computer Science department
        try:
            # Get the department by name
            cs_dept = Department.objects.get(name="Computer Science")
            # Use the department object for filtering
            subjects = Subject.objects.filter(department=cs_dept)
        except Department.DoesNotExist:
            messages.error(request, 'Department "Computer Science" not found. Please contact the administrator.')
            return redirect('hod_dashboard')
    else:
        subjects = Subject.objects.filter(staff=request.user)
    
    # Get all classes for today
    today = timezone.now().date()
    classes = Class.objects.filter(
        subject__in=subjects,
        date=today
    ).select_related('subject')
    
    # Check if subject and date are provided in the request
    subject_id = request.GET.get('subject')
    date_str = request.GET.get('date')
    
    # Initialize available_classes as None
    available_classes = None
    
    # If both subject and date are provided, get available classes
    if subject_id and date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            available_classes = Class.objects.filter(
                subject_id=subject_id,
                date=selected_date
            ).order_by('start_time')
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        class_date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        class_id = request.POST.get('class_id')
        
        if subject_id and class_date:
            subject = get_object_or_404(Subject, id=subject_id)
            
            # Check if we're using an existing class or creating a new one
            if class_id:
                try:
                    class_obj = Class.objects.get(id=class_id)
                except Class.DoesNotExist:
                    messages.error(request, 'Class not found.')
                    return redirect('mark_attendance')
            else:
                # Create a new class session if start_time and end_time are provided
                if start_time and end_time:
                    try:
                        class_obj, created = Class.objects.get_or_create(
                            subject=subject,
                            date=datetime.strptime(class_date, '%Y-%m-%d').date(),
                            defaults={
                                'start_time': datetime.strptime(start_time, '%H:%M').time(),
                                'end_time': datetime.strptime(end_time, '%H:%M').time(),
                            }
                        )
                        
                        if not created:
                            messages.info(request, 'A class session already exists for this subject and date.')
                        else:
                            messages.success(request, 'Class session created successfully.')
                    except Exception as e:
                        messages.error(request, f'Error creating class session: {str(e)}')
                        return redirect('mark_attendance')
                else:
                    messages.error(request, 'Start time and end time are required.')
                    return redirect('mark_attendance')
            
            # Redirect to take attendance page with appropriate URL
            url_kwargs = {'subject_id': subject.id}
            url_name = 'take_attendance'
            
            # Add query parameters for the date and class_id
            redirect_url = reverse(url_name, kwargs=url_kwargs)
            query_params = {}
            
            if class_date:
                query_params['date'] = class_date
            
            if class_id:
                query_params['class_id'] = class_id
            
            if query_params:
                redirect_url = f"{redirect_url}?{urlencode(query_params)}"
            
            return redirect(redirect_url)
    
    context = {
        'subjects': subjects,
        'today': today,
        'classes': classes,
        'available_classes': available_classes,
        'page_title': 'Mark Attendance'
    }
    return render(request, 'accounts/mark_attendance.html', context)

@login_required
def take_attendance(request, subject_id, date=None):
    """View for staff to take attendance for a specific subject on a specific date"""
    if request.user.user_type != 'staff' and request.user.user_type != 'hod':
        messages.error(request, 'Access denied. Staff or HOD access only.')
        return redirect('login')
    
    # Import the correct models from the attendance app
    from attendance.models import Subject, Class, Attendance, Department
    
    # Check if the subject exists
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Staff can only take attendance for subjects they teach
    # HOD can take attendance for subjects in their department
    if request.user.user_type == 'staff' and subject.staff != request.user:
        messages.error(request, 'You are not authorized to take attendance for this subject.')
        return redirect('mark_attendance')
    elif request.user.user_type == 'hod':
        # For HOD users, directly get the Computer Science department
        try:
            # Get the department by name
            cs_dept = Department.objects.get(name="Computer Science")
            # Check if the subject belongs to the HOD's department
            if subject.department.id != cs_dept.id:
                messages.error(request, 'You are not authorized to take attendance for subjects outside your department.')
                return redirect('mark_attendance')
        except Department.DoesNotExist:
            messages.error(request, 'Department "Computer Science" not found. Please contact the administrator.')
            return redirect('hod_dashboard')
    
    # If date is not provided in the URL, check if it's in the query parameters
    if date is None:
        date = request.GET.get('date')
    
    # If date is provided, parse it
    if date:
        try:
            attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect('mark_attendance')
    else:
        attendance_date = timezone.now().date()
    
    # Get all students for this subject's semester
    students = CustomUser.objects.filter(
        user_type='student',
        semester=subject.semester
    ).order_by('first_name', 'last_name')
    
    # Check if a specific class_id is provided
    class_id = request.GET.get('class_id')
    
    # Check if a class session already exists
    if class_id:
        try:
            class_obj = Class.objects.get(id=class_id)
            existing = True
        except Class.DoesNotExist:
            class_obj = None
            existing = False
    else:
        try:
            class_obj = Class.objects.get(subject=subject, date=attendance_date)
            existing = True
        except Class.DoesNotExist:
            class_obj = None
            existing = False
    
    # Handle POST request (save attendance)
    if request.method == 'POST':
        # Make sure we have a class object
        if not class_obj:
            # Create a new class session
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            
            if start_time and end_time:
                try:
                    class_obj = Class.objects.create(
                        subject=subject,
                        date=attendance_date,
                        start_time=datetime.strptime(start_time, '%H:%M').time(),
                        end_time=datetime.strptime(end_time, '%H:%M').time()
                    )
                    messages.success(request, 'Class session created successfully.')
                except Exception as e:
                    messages.error(request, f'Error creating class session: {str(e)}')
                    return redirect('mark_attendance')
            else:
                messages.error(request, 'Start time and end time are required.')
                return redirect('mark_attendance')
        
        # Save attendance records for each student
        attendance_saved = False
        
        for student in students:
            attendance_value = request.POST.get(f'student_{student.id}')
            is_present = attendance_value == 'present'
            
            # Get or create attendance record
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                class_session=class_obj,
                defaults={
                    'is_present': is_present,
                    'marked_by': request.user,
                    'marked_at': timezone.now()
                }
            )
            
            attendance_saved = True
        
        if attendance_saved:
            messages.success(request, 'Attendance saved successfully!')
            return redirect('mark_attendance')
    
    # Get existing attendance records if any
    attendance_records = {}
    if existing and class_obj:
        records = Attendance.objects.filter(class_session=class_obj)
        for record in records:
            attendance_records[record.student_id] = record.is_present
    
    context = {
        'subject': subject,
        'students': students,
        'class_date': attendance_date,
        'class_obj': class_obj,
        'existing': existing,
        'attendance_records': attendance_records,
        'page_title': f'Take Attendance - {subject.name}'
    }
    
    return render(request, 'accounts/take_attendance.html', context)
