from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count
from .models import Subject, Class, Attendance, LeaveRequest
from .forms import SubjectForm, ClassForm, AttendanceForm, LeaveRequestForm
from accounts.models import CustomUser
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.db import transaction

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 'staff'

class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'attendance/subject_list.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        if self.request.user.user_type == 'staff':
            return Subject.objects.filter(staff=self.request.user)
        return Subject.objects.all()

class SubjectCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'attendance/subject_form.html'
    success_url = reverse_lazy('subject_list')

    def form_valid(self, form):
        form.instance.staff = self.request.user
        return super().form_valid(form)

class ClassCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Class
    form_class = ClassForm
    template_name = 'attendance/class_form.html'
    success_url = reverse_lazy('subject_list')

@login_required
def take_attendance(request, class_id):
    class_session = get_object_or_404(Class, id=class_id)
    if request.user != class_session.subject.staff:
        messages.error(request, 'You are not authorized to take attendance for this class.')
        return redirect('subject_list')

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance marked successfully!')
            return redirect('subject_list')
    else:
        form = AttendanceForm(initial={'class_session': class_session})

    return render(request, 'attendance/take_attendance.html', {
        'form': form,
        'class_session': class_session
    })

class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'

    def get_queryset(self):
        if self.request.user.user_type == 'staff':
            return Attendance.objects.filter(class_session__subject__staff=self.request.user)
        elif self.request.user.user_type == 'hod':
            return Attendance.objects.filter(class_session__subject__department=self.request.user.department_managed)
        return Attendance.objects.filter(student=self.request.user)

def home(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'staff':
            return redirect('staff_dashboard')
        elif request.user.user_type == 'student':
            return redirect('student_dashboard')
        else:
            return redirect('admin_dashboard')
    return render(request, 'attendance/home.html')

@login_required
def staff_dashboard(request):
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    subjects = Subject.objects.filter(staff=request.user)
    today_classes = Class.objects.filter(
        subject__in=subjects,
        date=timezone.now().date()
    )
    upcoming_classes = Class.objects.filter(
        subject__in=subjects,
        date__gt=timezone.now().date()
    ).order_by('date', 'start_time')[:5]
    
    context = {
        'subjects': subjects,
        'today_classes': today_classes,
        'upcoming_classes': upcoming_classes,
    }
    return render(request, 'attendance/staff_dashboard.html', context)

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied. Students only.')
        return redirect('home')
    
    today_classes = Class.objects.filter(
        subject__semester=request.user.semester,
        date=timezone.now().date()
    )
    upcoming_classes = Class.objects.filter(
        subject__semester=request.user.semester,
        date__gt=timezone.now().date()
    ).order_by('date', 'start_time')[:5]
    
    attendance_summary = Attendance.objects.filter(
        student=request.user,
        class_session__date__gte=timezone.now().date() - timezone.timedelta(days=30)
    ).values('class_session__subject__name').annotate(
        total_classes=Count('id'),
        present_classes=Count('id', filter=Q(is_present=True))
    )
    
    context = {
        'today_classes': today_classes,
        'upcoming_classes': upcoming_classes,
        'attendance_summary': attendance_summary,
    }
    return render(request, 'attendance/student_dashboard.html', context)

class ClassListView(LoginRequiredMixin, ListView):
    model = Class
    template_name = 'attendance/class_list.html'
    context_object_name = 'classes'
    
    def get_queryset(self):
        if self.request.user.user_type == 'staff':
            return Class.objects.filter(subject__staff=self.request.user)
        else:
            return Class.objects.filter(subject__semester=self.request.user.semester)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.filter(staff=self.request.user) if self.request.user.user_type == 'staff' else Subject.objects.filter(semester=self.request.user.semester)
        return context

class ClassDetailView(LoginRequiredMixin, DetailView):
    model = Class
    template_name = 'attendance/class_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_type == 'staff':
            context['students'] = CustomUser.objects.filter(
                user_type='student',
                semester=self.object.subject.semester
            )
            context['attendances'] = Attendance.objects.filter(class_session=self.object)
        else:
            context['attendance'] = Attendance.objects.filter(
                class_session=self.object,
                student=self.request.user
            ).first()
        return context

@login_required
def mark_attendance(request, class_id=None):
    if not request.user.user_type == 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    # Get today's date
    today = timezone.now().date()
    
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        class_session = get_object_or_404(Class, id=class_id, subject__staff=request.user)
        student_attendance = request.POST.getlist('attendance[]')
        remarks = request.POST.getlist('remarks[]')
        
        try:
            with transaction.atomic():
                # Clear existing attendance for this class to avoid duplicates
                Attendance.objects.filter(class_session=class_session).delete()
                
                # Create new attendance records
                for student_data in zip(student_attendance, remarks):
                    student_id, is_present = student_data[0].split('_')
                    student = CustomUser.objects.get(id=student_id)
                    remark = student_data[1]
                    
                    Attendance.objects.create(
                        student=student,
                        class_session=class_session,
                        is_present=is_present == 'present',
                        marked_by=request.user,
                        remarks=remark
                    )
                
                messages.success(request, 'Attendance marked successfully!')
                return redirect('staff_dashboard')
                
        except Exception as e:
            messages.error(request, f'Error marking attendance: {str(e)}')
            return redirect('mark_attendance')
    
    # For GET request, show the attendance form
    if class_id:
        # Show attendance form for specific class
        class_session = get_object_or_404(Class, id=class_id, subject__staff=request.user)
        students = CustomUser.objects.filter(user_type='student')
        existing_attendance = {
            att.student_id: {
                'is_present': att.is_present,
                'remarks': att.remarks
            } for att in Attendance.objects.filter(class_session=class_session)
        }
    else:
        # Show list of today's classes
        class_session = None
        students = None
        existing_attendance = None
        
    classes = Class.objects.filter(
        subject__staff=request.user,
        date=today,
        is_cancelled=False
    ).select_related('subject')
    
    context = {
        'classes': classes,
        'selected_class': class_session,
        'students': students,
        'existing_attendance': existing_attendance,
        'today_date': today.strftime('%d %B %Y'),
    }
    
    return render(request, 'attendance/mark_attendance.html', context)

@login_required
def view_attendance(request, class_id):
    if not request.user.user_type == 'staff':
        messages.error(request, 'Access denied. Staff access only.')
        return redirect('login')
    
    class_session = get_object_or_404(Class, id=class_id, subject__staff=request.user)
    attendance_records = Attendance.objects.filter(class_session=class_session).select_related('student')
    
    context = {
        'class_session': class_session,
        'attendance_records': attendance_records,
    }
    
    return render(request, 'attendance/view_attendance.html', context)

class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    template_name = 'attendance/leave_request_form.html'
    fields = ['subject', 'leave_type', 'start_date', 'end_date', 'reason']
    
    def form_valid(self, form):
        form.instance.student = self.request.user
        messages.success(self.request, 'Leave request submitted successfully!')
        return super().form_valid(form)

class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'attendance/leave_request_list.html'
    context_object_name = 'leave_requests'
    
    def get_queryset(self):
        if self.request.user.user_type == 'staff':
            return LeaveRequest.objects.filter(subject__staff=self.request.user)
        else:
            return LeaveRequest.objects.filter(student=self.request.user)

@login_required
def approve_leave_request(request, pk):
    if request.user.user_type != 'staff':
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if leave_request.subject.staff != request.user:
        messages.error(request, 'You are not authorized to approve this leave request.')
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approve', 'reject']:
            leave_request.status = 'approved' if action == 'approve' else 'rejected'
            leave_request.approved_by = request.user
            leave_request.approved_at = timezone.now()
            leave_request.save()
            
            messages.success(request, f'Leave request {action}ed successfully!')
            return redirect('leave_request_list')
    
    return render(request, 'attendance/approve_leave.html', {'leave_request': leave_request})

def login_choice(request):
    """Landing page for choosing between student and staff login."""
    return render(request, 'accounts/login_choice.html')

def student_login(request):
    """Handle student login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.user_type == 'student':
            login(request, user)
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/student_login.html')

def staff_login(request):
    """Handle staff login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.user_type == 'staff':
            login(request, user)
            return redirect('staff_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/staff_login.html')
