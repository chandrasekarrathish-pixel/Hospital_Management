from django import forms
from .models import MedicalRecord, Prescription, LabReport

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment_notes']
        widgets = {
            'diagnosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Acute Bronchitis'}),
            'treatment_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed treatment plan and notes...'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type medications here...'
            }),
        }

class LabReportForm(forms.ModelForm):
    class Meta:
        model = LabReport
        fields = ['test_name', 'report_file']
        widgets = {
            'test_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Complete Blood Count (CBC)'}),
            'report_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
        }