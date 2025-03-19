from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.home, name='home'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),
    path('classes/<int:class_id>/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('leave/request/', views.LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('leave/list/', views.LeaveRequestListView.as_view(), name='leave_request_list'),
    path('leave/<int:pk>/approve/', views.approve_leave_request, name='approve_leave'),
    path('login/', views.login_choice, name='login_choice'),
    path('student/login/', views.student_login, name='student_login'),
    path('staff/login/', views.staff_login, name='staff_login'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('mark/<int:class_id>/', views.mark_attendance, name='mark_attendance'),
    path('view/<int:class_id>/', views.view_attendance, name='view_attendance'),
] 