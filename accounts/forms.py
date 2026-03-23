from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from patients.models import Patient

class PatientSignUpForm(UserCreationForm):
    # Adding some basic profile fields to the registration form
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True # Automatically assign the Patient role
        if commit:
            user.save()
            # Automatically create the linked Patient profile
            Patient.objects.create(user=user)
        return user