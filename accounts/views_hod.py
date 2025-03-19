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
    staff_members = CustomUser.objects.filter(
        department=department,
        user_type='staff'
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_staff':
            staff_id = request.POST.get('staff_id')
            staff = get_object_or_404(CustomUser, id=staff_id)
            
            staff.designation = request.POST.get('designation', staff.designation)
            staff.qualification = request.POST.get('qualification', staff.qualification)
            staff.specialization = request.POST.get('specialization', staff.specialization)
            staff.office_location = request.POST.get('office_location', staff.office_location)
            
            try:
                staff.save()
                messages.success(request, f'Staff member {staff.get_full_name()} updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating staff member: {str(e)}')
    
    context = {
        'staff_members': staff_members,
    }
    return render(request, 'accounts/hod/manage_staff.html', context)

@login_required
@user_passes_test(is_hod)
def view_subject_details(request, subject_id):
    department = request.user.department_managed
    subject = get_object_or_404(Subject, id=subject_id, department=department)
    
    # Get staff members for the department
    staff_members = CustomUser.objects.filter(
        department=department,
        user_type='staff'
    )
    
    # Calculate statistics
    enrolled_students = CustomUser.objects.filter(
        department=department,
        user_type='student',
        semester=subject.semester
    )
    
    # Calculate average attendance
    attendance_records = UserAttendance.objects.filter(subject=subject)
    total_attendance = attendance_records.count()
    present_count = attendance_records.filter(is_present=True).count()
    average_attendance = round((present_count / total_attendance * 100) if total_attendance > 0 else 0, 1)
    
    # Get assignments count
    assignments_count = Assignment.objects.filter(subject=subject).count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign_staff':
            staff_id = request.POST.get('staff_id')
            try:
                staff = CustomUser.objects.get(id=staff_id)
                subject.staff = staff
                subject.save()
                messages.success(request, f'Staff assigned to {subject.name} successfully!')
            except Exception as e:
                messages.error(request, f'Error assigning staff: {str(e)}')
    
    context = {
        'subject': subject,
        'assigned_staff': subject.staff,
        'staff_members': staff_members,
        'enrolled_students_count': enrolled_students.count(),
        'average_attendance': average_attendance,
        'assignments_count': assignments_count,
    }
    return render(request, 'accounts/hod/subject_details.html', context) 