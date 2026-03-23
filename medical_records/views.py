from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from patients.models import Patient
from doctors.models import Doctor
from .forms import LabReportForm
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Prescription


@login_required
def download_prescription(request, rx_id):
    # Fetch the prescription using the ID from the URL
    # We use 'rx' as the key in the dictionary to match the template
    prescription_obj = get_object_or_404(Prescription, id=rx_id)

    return render(request, 'medical_records/prescription_print.html', {
        'rx': prescription_obj
    })

def upload_lab_report(request, patient_id):
    # Security: Only Admins and Doctors can upload lab reports
    if not (request.user.is_admin or request.user.is_superuser or request.user.is_doctor):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        # request.FILES is mandatory for handling the actual PDF/Image file
        form = LabReportForm(request.POST, request.FILES)
        if form.is_valid():
            lab_report = form.save(commit=False)
            lab_report.patient = patient

            # If a doctor is uploading this, link their name to the report
            if request.user.is_doctor:
                lab_report.doctor = Doctor.objects.get(user=request.user)

            lab_report.save()
            messages.success(request, f"Lab report '{lab_report.test_name}' uploaded successfully.")

            # Route back based on who uploaded it
            if request.user.is_doctor:
                return redirect('patient_detail', patient_id=patient.id)
            return redirect('admin_dashboard')
    else:
        form = LabReportForm()

    return render(request, 'medical_records/upload_lab.html', {'form': form, 'patient': patient})