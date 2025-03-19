from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Department, Experience, Education, Publication, Assignment, Subject, AssignmentSubmission
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your college email'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    student_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Student ID'
        })
    )
    
    semester = forms.ChoiceField(
        choices=[
            ('', 'Select Semester'),
            ('1', 'Semester 1'),
            ('2', 'Semester 2'),
            ('3', 'Semester 3'),
            ('4', 'Semester 4'),
            ('5', 'Semester 5'),
            ('6', 'Semester 6'),
            ('7', 'Semester 7'),
            ('8', 'Semester 8'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Select your date of birth'
        })
    )
    
    address = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your address',
            'rows': 3
        })
    )
    
    blood_group = forms.ChoiceField(
        choices=[
            ('', 'Select Blood Group'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    emergency_contact = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter emergency contact number'
        })
    )
    
    parent_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter parent/guardian name'
        })
    )
    
    parent_phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter parent/guardian phone number'
        })
    )
    
    academic_year = forms.ChoiceField(
        choices=[
            ('', 'Select Academic Year'),
            ('2024-25', '2024-25'),
            ('2023-24', '2023-24'),
            ('2022-23', '2022-23'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        
        # List of allowed email domains
        allowed_domains = [
            'college.edu',  # Example college domain
            'university.edu',  # Example university domain
            'student.edu',  # Example student domain
            'gmail.com',    # Allow gmail for testing
            'yahoo.com',    # Allow yahoo for testing
            'outlook.com'   # Allow outlook for testing
        ]
        
        # Get the domain part of the email
        domain = email.split('@')[-1].lower()
        
        if not any(domain.endswith(allowed) for allowed in allowed_domains):
            raise forms.ValidationError(_(
                'Please use a valid email address. Allowed domains are: ' + 
                ', '.join(allowed_domains)
            ))
        
        return email
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if User.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError(_('This Student ID is already registered.'))
        return student_id
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'department', 
                 'student_id', 'semester', 'phone_number', 'date_of_birth', 
                 'address', 'blood_group', 'emergency_contact', 'parent_name',
                 'parent_phone', 'academic_year', 'profile_picture',
                 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        if commit:
            user.save()
        return user

class StaffRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your college email'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    staff_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Staff ID'
        })
    )
    
    designation = forms.ChoiceField(
        choices=[
            ('', 'Select Designation'),
            ('professor', 'Professor'),
            ('associate_professor', 'Associate Professor'),
            ('assistant_professor', 'Assistant Professor'),
            ('lecturer', 'Lecturer'),
            ('lab_instructor', 'Lab Instructor'),
            ('administrative', 'Administrative Staff'),
            ('librarian', 'Librarian'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    
    date_of_joining = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Select date of joining'
        })
    )
    
    qualification = forms.ChoiceField(
        choices=[
            ('', 'Select Qualification'),
            ('phd', 'Ph.D.'),
            ('mtech', 'M.Tech'),
            ('mba', 'MBA'),
            ('mca', 'MCA'),
            ('mcom', 'M.Com'),
            ('ma', 'M.A.'),
            ('msc', 'M.Sc.'),
            ('btech', 'B.Tech'),
            ('bca', 'BCA'),
            ('bba', 'BBA'),
            ('bcom', 'B.Com'),
            ('ba', 'B.A.'),
            ('bsc', 'B.Sc.'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    specialization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your specialization'
        })
    )
    
    office_location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your office location'
        })
    )
    
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        
        # List of allowed email domains
        allowed_domains = [
            'college.edu',  # Example college domain
            'university.edu',  # Example university domain
            'student.edu',  # Example student domain
            'gmail.com',    # Allow gmail for testing
            'yahoo.com',    # Allow yahoo for testing
            'outlook.com'   # Allow outlook for testing
        ]
        
        # Get the domain part of the email
        domain = email.split('@')[-1].lower()
        
        if not any(domain.endswith(allowed) for allowed in allowed_domains):
            raise forms.ValidationError(_(
                'Please use a valid email address. Allowed domains are: ' + 
                ', '.join(allowed_domains)
            ))
        
        return email
    
    def clean_staff_id(self):
        staff_id = self.cleaned_data.get('staff_id')
        if User.objects.filter(staff_id=staff_id).exists():
            raise forms.ValidationError(_('This Staff ID is already registered.'))
        return staff_id
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'department', 
                 'staff_id', 'designation', 'phone_number', 'date_of_joining',
                 'qualification', 'specialization', 'office_location',
                 'profile_picture', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'staff'
        if commit:
            user.save()
        return user

class CollegeRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your college email'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        
        # List of allowed email domains
        allowed_domains = [
            'college.edu',  # Example college domain
            'university.edu',  # Example university domain
            'student.edu',  # Example student domain
            'gmail.com',    # Allow gmail for testing
            'yahoo.com',    # Allow yahoo for testing
            'outlook.com'   # Allow outlook for testing
        ]
        
        # Get the domain part of the email
        domain = email.split('@')[-1].lower()
        
        if not any(domain.endswith(allowed) for allowed in allowed_domains):
            raise forms.ValidationError(_(
                'Please use a valid email address. Allowed domains are: ' + 
                ', '.join(allowed_domains)
            ))
        
        return email
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'department', 'designation', 'qualification', 'specialization',
            'office_location', 'bio', 'skills', 'profile_picture'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g. Python, Data Analysis, Machine Learning'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['position', 'organization', 'start_date', 'end_date', 'current', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['current'].widget.attrs.update({'class': 'form-check-input'})
        
    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get('current')
        end_date = cleaned_data.get('end_date')
        
        if current and end_date:
            self.add_error('end_date', 'End date should be empty if this is your current position.')
        elif not current and not end_date:
            self.add_error('end_date', 'End date is required if this is not your current position.')
            
        return cleaned_data

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_year', 'end_year', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')
        
        if start_year and end_year and start_year > end_year:
            self.add_error('end_year', 'End year cannot be before start year.')
            
        return cleaned_data

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'authors', 'journal', 'year', 'url']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'due_date', 'max_marks', 'file_attachment']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.user_type == 'staff':
            # Only show subjects taught by this staff member
            self.fields['subject'].queryset = Subject.objects.filter(staff=user)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class AssignmentGradingForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['marks', 'feedback', 'status']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    def clean_marks(self):
        marks = self.cleaned_data.get('marks')
        max_marks = self.instance.assignment.max_marks
        if marks > max_marks:
            raise forms.ValidationError(f"Marks cannot exceed maximum marks ({max_marks}).")
        return marks

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_text', 'submission_file']
        widgets = {
            'submission_text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter your answer or comments here...'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'}) 