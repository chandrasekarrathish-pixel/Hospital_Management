from django.db import models
from django.conf import settings


class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    # TextField allows for longer medical history notes
    medical_history = models.TextField(blank=True, help_text="Past illnesses, allergies, etc.")
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/patients/', null=True, blank=True)
    def __str__(self):
        return self.user.get_full_name() or self.user.username