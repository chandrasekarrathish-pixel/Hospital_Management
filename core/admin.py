from django.contrib import admin
from .models import Department

# This single line makes the table visible in the Admin Panel
admin.site.register(Department)