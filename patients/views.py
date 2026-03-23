from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from .forms import PatientProfileForm
from medical_records.models import MedicalRecord, Prescription, LabReport
from django.shortcuts import render, redirect, get_object_or_404


@login_required
def edit_profile(request):
    if not request.user.is_patient:
        return redirect('home')

    patient = Patient.objects.get(user=request.user)

    if request.method == 'POST':
        # request.FILES is required because we are uploading an image (profile picture)
        form = PatientProfileForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=patient)

    return render(request, 'patients/edit_profile.html', {'form': form})


@login_required
def my_records(request):
    """Fetches all medical history related to the logged-in patient."""

    # NEW CHECK: Try to get the patient profile.
    # If it doesn't exist, we'll handle it gracefully instead of redirecting.
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        # If you are an admin/superuser without a Patient profile,
        # we show the page but with empty lists so it doesn't crash.
        messages.warning(request, "No patient profile found for this account.")
        return render(request, 'patients/my_records.html', {
            'records': [],
            'prescriptions': [],
            'lab_reports': []
        })

    # If we found the patient, get their data
    context = {
        'records': MedicalRecord.objects.filter(patient=patient).order_by('-date_recorded'),
        'prescriptions': Prescription.objects.filter(patient=patient).order_by('-date_issued'),
        'lab_reports': LabReport.objects.filter(patient=patient).order_by('-generated_on'),
    }
    return render(request, 'patients/my_records.html', context)