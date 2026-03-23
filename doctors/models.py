from django.db import models
from django.conf import settings
from core.models import Department  # Make sure this import is here!


class Doctor(models.Model):
    objects = None
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # THIS IS THE FIELD IT IS LOOKING FOR:
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    specialization = models.CharField(max_length=150)
    profile_picture = models.ImageField(upload_to='profile_pics/doctors/', null=True, blank=True)
    available_days = models.CharField(max_length=100, help_text="e.g., Mon, Wed, Fri")

    def __str__(self):
        # We also added a safety check here in case department is null
        dept_name = self.department.name if self.department else "General"
        return f"Dr. {self.user.get_full_name()} - {dept_name}"