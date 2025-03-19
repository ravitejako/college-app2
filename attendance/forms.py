from django import forms
from .models import Subject, Class, Attendance, LeaveRequest
from accounts.models import CustomUser

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code']

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['subject', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'is_present']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'class_session' in kwargs.get('initial', {}):
            class_session = kwargs['initial']['class_session']
            self.fields['student'].queryset = CustomUser.objects.filter(user_type='student')

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['subject', 'leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        } 