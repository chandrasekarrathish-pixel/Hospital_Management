from django.db import models
from patients.models import Patient
from doctors.models import Doctor

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    diagnosis = models.CharField(max_length=255)
    treatment_notes = models.TextField()
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.patient} on {self.date_recorded.date()}"

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, help_text="Dosage and instructions")
    date_issued = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription by {self.doctor} for {self.patient}"

class LabReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    test_name = models.CharField(max_length=150)
    report_file = models.FileField(upload_to='lab_reports/')
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_name} - {self.patient}"