from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # This adds the checkboxes to the "Personal Info" or "Permissions" section in Admin
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_doctor', 'is_patient')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Roles', {'fields': ('is_doctor', 'is_patient')}),
    )
# This tells Django to use the standard User interface for our CustomUser

admin.site.register(CustomUser, CustomUserAdmin)