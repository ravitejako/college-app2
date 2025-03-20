from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import CustomUser, Subject, Department, UserAttendance, Assignment
from django.db.models import Q, Avg, Count
from django.db.models.functions import TruncDate

def is_hod(user):
    return user.is_authenticated and user.user_type == 'hod' and user.is_department_head

@login_required
@user_passes_test(is_hod)
def hod_dashboard(request):
    department = request.user.department_managed
    staff_members = CustomUser.objects.filter(
        department=department,
        user_type='staff'
    )
    subjects = Subject.objects.filter(department=department)
    
    context = {
        'staff_count': staff_members.count(),
        'subject_count': subjects.count(),
        'assigned_subjects_count': subjects.exclude(staff=None).count(),
        'unassigned_subjects_count': subjects.filter(staff=None).count(),
        'staff_members': staff_members[:5],  # Show latest 5 staff members
        'subjects': subjects[:5],  # Show latest 5 subjects
    }
    return render(request, 'accounts/hod/dashboard.html', context)

@login_required
@user_passes_test(is_hod)
def manage_subjects(request):
    department = request.user.department_managed
    subjects = Subject.objects.filter(department=department)
    staff_members = CustomUser.objects.filter(
        department=department,
        user_type='staff'
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_subject':
            code = request.POST.get('code')
            name = request.POST.get('name')
            semester = request.POST.get('semester')
            credits = request.POST.get('credits')
            staff_id = request.POST.get('staff')
            description = request.POST.get('description', '')
            
            try:
                staff = CustomUser.objects.get(id=staff_id) if staff_id else None
                Subject.objects.create(
                    code=code,
                    name=name,
                    department=department,
                    semester=semester,
                    credits=credits,
                    staff=staff,
                    description=description
                )
                messages.success(request, 'Subject added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding subject: {str(e)}')
        
        elif action == 'assign_staff':
            subject_id = request.POST.get('subject_id')
            staff_id = request.POST.get('staff_id')
            
            try:
                subject = Subject.objects.get(id=subject_id)
                staff = CustomUser.objects.get(id=staff_id)
                subject.staff = staff
                subject.save()
                messages.success(request, f'Staff assigned to {subject.name} successfully!')
            except Exception as e:
                messages.error(request, f'Error assigning staff: {str(e)}')
                
        elif action == 'delete_subject':
            subject_id = request.POST.get('subject_id')
            
            try:
                subject = Subject.objects.get(id=subject_id, department=department)
                subject_name = subject.name
                subject.delete()
                messages.success(request, f'Subject "{subject_name}" has been deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting subject: {str(e)}')
                
        elif action == 'bulk_assign_staff':
            subject_ids = request.POST.get('subject_ids', '').split(',')
            staff_id = request.POST.get('staff_id')
            
            if subject_ids and staff_id:
                try:
                    staff = CustomUser.objects.get(id=staff_id)
                    updated_count = 0
                    
                    for subject_id in subject_ids:
                        if subject_id.strip():
                            try:
                                subject = Subject.objects.get(id=int(subject_id.strip()), department=department)
                                subject.staff = staff
                                subject.save()
                                updated_count += 1
                            except (Subject.DoesNotExist, ValueError):
                                continue
                    
                    if updated_count > 0:
                        messages.success(request, f'Successfully assigned {staff.get_full_name()} to {updated_count} subject(s)!')
                    else:
                        messages.warning(request, 'No subjects were updated.')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'The selected staff member does not exist.')
            else:
                messages.error(request, 'Please select both subjects and a staff member.')
                
        elif action == 'edit_subject':
            subject_id = request.POST.get('subject_id')
            code = request.POST.get('code')
            name = request.POST.get('name')
            semester = request.POST.get('semester')
            credits = request.POST.get('credits')
            description = request.POST.get('description', '')
            
            try:
                subject = Subject.objects.get(id=subject_id, department=department)
                subject.code = code
                subject.name = name
                subject.semester = semester
                subject.credits = credits
                subject.description = description
                subject.save()
                messages.success(request, f'Subject "{name}" has been updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating subject: {str(e)}')
                
    context = {
        'subjects': subjects,
        'staff_members': staff_members,
        'assigned_count': subjects.exclude(staff=None).count(),
        'unassigned_count': subjects.filter(staff=None).count(),
    }
    return render(request, 'accounts/hod/manage_subjects.html', context)

@login_required
@user_passes_test(is_hod)
def manage_staff(request):
    department = request.user.department_managed
    staff_list = CustomUser.objects.filter(
        department=department,
        user_type='staff'
    )
    
    # Get counts for different staff designations
    professors_count = staff_list.filter(designation__contains='Professor').count()
    lecturers_count = staff_list.filter(designation='Lecturer').count()
    
    # Get list of unique specializations for the filter
    specializations = staff_list.exclude(specialization__isnull=True).exclude(specialization='').values_list('specialization', flat=True).distinct()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_staff':
            # Handle staff update
            staff_id = request.POST.get('staff_id')
            designation = request.POST.get('designation')
            qualification = request.POST.get('qualification')
            specialization = request.POST.get('specialization')
            office_location = request.POST.get('office_location')
            
            try:
                staff = CustomUser.objects.get(id=staff_id, user_type='staff', department=department)
                staff.designation = designation
                staff.qualification = qualification
                staff.specialization = specialization
                staff.office_location = office_location
                staff.save()
                messages.success(request, f"Staff member {staff.get_full_name()} updated successfully!")
            except CustomUser.DoesNotExist:
                messages.error(request, "Staff member not found.")
        
        elif action == 'add_staff':
            # Handle adding new staff
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            staff_id = request.POST.get('staff_id')
            designation = request.POST.get('designation')
            qualification = request.POST.get('qualification')
            specialization = request.POST.get('specialization')
            office_location = request.POST.get('office_location')
            password = request.POST.get('password')
            
            try:
                # Check if user with this email already exists
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, f"User with email {email} already exists.")
                else:
                    new_staff = CustomUser.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        user_type='staff',
                        department=department,
                        staff_id=staff_id,
                        designation=designation,
                        qualification=qualification,
                        specialization=specialization,
                        office_location=office_location
                    )
                    messages.success(request, f"Staff member {new_staff.get_full_name()} added successfully!")
            except Exception as e:
                messages.error(request, f"Error adding staff member: {str(e)}")
    
    context = {
        'staff_list': staff_list,
        'professors_count': professors_count,
        'lecturers_count': lecturers_count,
        'specializations': specializations,
    }
    return render(request, 'accounts/hod/manage_staff.html', context)

@login_required
@user_passes_test(is_hod)
def view_subject_details(request, subject_id):
    department = request.user.department_managed
    subject = get_object_or_404(Subject, id=subject_id, department=department)
    staff_members = CustomUser.objects.filter(
        department=department,
        user_type='staff'
    )
    
    # Mock data for schedule items since we don't have a real model yet
    schedule_items = [
        {
            'day_of_week': 'Monday',
            'start_time': '09:00 AM',
            'end_time': '10:30 AM',
            'room': 'Room 101'
        },
        {
            'day_of_week': 'Wednesday',
            'start_time': '11:00 AM',
            'end_time': '12:30 PM',
            'room': 'Room 203'
        }
    ]
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign_staff':
            staff_id = request.POST.get('staff_id')
            
            try:
                if staff_id:
                    staff = CustomUser.objects.get(id=staff_id, user_type='staff')
                    subject.staff = staff
                    subject.save()
                    messages.success(request, f'Successfully assigned {staff.get_full_name()} to {subject.name}!')
                else:
                    subject.staff = None
                    subject.save()
                    messages.success(request, f'Removed staff assignment from {subject.name}!')
                    
                return redirect('hod_view_subject_details', subject_id=subject.id)
            except CustomUser.DoesNotExist:
                messages.error(request, 'Staff member not found.')
    
    # Count enrolled students (not implemented yet)
    enrolled_students_count = 0
    
    # Calculate average attendance (not implemented yet)
    average_attendance = 0
    
    # Count assignments (not implemented yet)
    assignments_count = 0
    
    context = {
        'subject': subject,
        'assigned_staff': subject.staff,
        'staff_members': staff_members,
        'enrolled_students_count': enrolled_students_count,
        'average_attendance': average_attendance,
        'assignments_count': assignments_count,
        'schedule_items': schedule_items,
    }
    
    return render(request, 'accounts/hod/subject_details.html', context)

@login_required
@user_passes_test(is_hod)
def staff_directory(request):
    department = request.user.department_managed
    staff_members = CustomUser.objects.filter(
        department=department,
        user_type='staff'
    ).order_by('first_name')
    
    context = {
        'staff_members': staff_members,
    }
    return render(request, 'accounts/hod/staff.html', context)

def hod_exams(request):
    """
    View for the HOD to manage exams
    """
    context = {}
    return render(request, 'accounts/hod/hod_exams.html', context)

def hod_timetable(request):
    """
    View for the HOD to manage timetable
    """
    context = {}
    return render(request, 'accounts/hod/hod_timetable.html', context)

def hod_reports(request):
    """
    View for the HOD to view reports
    """
    context = {}
    return render(request, 'accounts/hod/hod_reports.html', context)

def hod_notifications(request):
    """
    View for the HOD to manage notifications
    """
    context = {}
    return render(request, 'accounts/hod/hod_notifications.html', context)

def hod_settings(request):
    """
    View for the HOD to manage settings
    """
    context = {}
    return render(request, 'accounts/hod/hod_settings.html', context) 