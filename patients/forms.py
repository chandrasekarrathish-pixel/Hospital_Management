from django import forms
from .models import Patient

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['date_of_birth', 'contact_number', 'address', 'blood_group', 'profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blood_group': forms.Select(
                choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')],
                attrs={'class': 'form-select'}
            ),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }