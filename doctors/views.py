from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from medical_records.models import MedicalRecord, Prescription
from medical_records.forms import MedicalRecordForm, PrescriptionForm
from dashboard.utils import create_notification
from core.models import Department
from django.db.models import Q
from medical_records.models import LabReport


@login_required
def doctor_dashboard(request):
    """The main landing page for doctors after login."""
    if not request.user.is_doctor:
        return redirect('home')

    doctor = get_object_or_404(Doctor, user=request.user)

    # Get today's appointments (Approved only)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='Approved'
    ).order_by('date', 'time')[:5]

    # Get pending appointment count to show a badge
    pending_count = Appointment.objects.filter(doctor=doctor, status='Pending').count()

    # Get the 5 most recent patients this doctor has treated
    recent_records = MedicalRecord.objects.filter(doctor=doctor).order_by('-date_recorded')
    recent_patients = []
    seen_ids = set()
    for rec in recent_records:
        if rec.patient.id not in seen_ids:
            recent_patients.append(rec.patient)
            seen_ids.add(rec.patient.id)
        if len(recent_patients) >= 5: break

    context = {
        'doctor': doctor,
        'upcoming_appointments': upcoming_appointments,
        'pending_count': pending_count,
        'recent_patients': recent_patients,
    }
    return render(request, 'dashboard/doctor.html', context)


@login_required
def my_patients(request):
    """Shows a list of unique patients who have booked this doctor."""
    if not request.user.is_doctor:
        return redirect('home')

    # 1. Get the doctor profile (using get_object_or_404 to avoid crashes)
    doctor = get_object_or_404(Doctor, user=request.user)

    # 2. LOGICAL FIX: Instead of a 'set', we filter Patients directly.
    # We find patients who have at least one appointment with this doctor.
    # .distinct() ensures each patient only appears once in the list.
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()

    return render(request, 'doctors/my_patients.html', {'patients': patients})


@login_required
def patient_detail(request, patient_id):
    """Shows the patient's medical history and forms to add new records."""
    if not request.user.is_doctor:
        return redirect('home')

    doctor = Doctor.objects.get(user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)
    # CORRECT
    records = MedicalRecord.objects.filter(patient=patient).order_by('-date_recorded')
    # Make sure this matches your LabReport model field name (e.g., 'created_at')
    # CORRECT
    lab_reports = LabReport.objects.filter(patient=patient).order_by('-generated_on')

    # Forms for adding new records
    record_form = MedicalRecordForm()
    prescription_form = PrescriptionForm()

    # Handle form submissions
    if request.method == 'POST':
        if 'submit_record' in request.POST:
            record_form = MedicalRecordForm(request.POST)
            if record_form.is_valid():
                record = record_form.save(commit=False)
                record.doctor = doctor
                record.patient = patient
                record.save()
                messages.success(request, "Diagnosis added successfully.")
                return redirect('patient_detail', patient_id=patient.id)

        elif 'submit_prescription' in request.POST:
            prescription_form = PrescriptionForm(request.POST)
            if prescription_form.is_valid():
                prescription = prescription_form.save(commit=False)
                prescription.doctor = doctor
                prescription.patient = patient
                prescription.notes = prescription_form.cleaned_data.get('notes')
                prescription.save()

                create_notification(patient.user,f"Dr. {doctor.user.last_name} has issued a new prescription for you. Check your records.")
                messages.success(request, "Prescription issued successfully.")
                return redirect('patient_detail', patient_id=patient.id)

    # Fetch history to display on the page
    context = {
        'patient': patient,
        'records': MedicalRecord.objects.filter(patient=patient).order_by('-date_recorded'),
        'prescriptions': Prescription.objects.filter(patient=patient).order_by('-date_issued'),
        'record_form': record_form,
        'prescription_form': prescription_form,
        # In doctors/views.py
        'lab_reports': LabReport.objects.filter(patient=patient).order_by('-generated_on'),
    }

    return render(request, 'doctors/patient_detail.html', context)


def doctor_list(request):
    doctors = Doctor.objects.all()
    # Replace 'Department' with whatever your actual department model is named if different!
    departments = Department.objects.all()

    # Grab what the user typed in the URL
    raw_search = request.GET.get('search', '')
    dept_filter = request.GET.get('department', '')

    # 1. HANDLE THE SMART SEARCH
    if raw_search:
        # Strip out "Dr.", "dr.", or "dr " so the database only looks for the actual name
        clean_search = raw_search.lower().replace('dr.', '').replace('dr ', '').strip()

        # Search username, first name, last name, OR specialization for partial matches!
        doctors = doctors.filter(
            Q(user__first_name__icontains=clean_search) |
            Q(user__last_name__icontains=clean_search) |
            Q(user__username__icontains=clean_search) |
            Q(specialization__icontains=clean_search)
        )

    # 2. HANDLE THE DEPARTMENT FILTER
    if dept_filter:
        doctors = doctors.filter(department_id=dept_filter)

    # Send the filtered doctors back to the HTML
    context = {
        'doctors': doctors,
        'departments': departments,
        'search_query': raw_search,  # Keeps their original text in the search box
        'dept_filter': dept_filter,
    }

    return render(request, 'doctors/doctor_list.html', context)