from django.contrib import admin
from .models import CustomUser, Department, Subject, UserAttendance, Result, Experience, Education, Publication

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(UserAttendance)
admin.site.register(Result)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Publication)
