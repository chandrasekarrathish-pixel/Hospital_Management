from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentForm
from patients.models import Patient
from doctors.models import Doctor
from dashboard.utils import create_notification


# --- PATIENT VIEWS ---

@login_required
def book_appointment(request, doctor=None):
    if not request.user.is_patient:
        messages.error(request, "Only patients can book appointments.")
        return redirect('home')

    patient = Patient.objects.get(user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            # Default status is 'Pending' from the model
            appointment.save()

            # FIXED: Grab the doctor directly from the saved appointment!
            create_notification(patient.user,
                                f"Your appointment request with Dr. {appointment.doctor.user.last_name} has been sent.")
            create_notification(appointment.doctor.user,
                                f"New appointment request from {patient.user.get_full_name()}.")

            messages.success(request, "Appointment requested successfully! Waiting for doctor approval.")
            return redirect('patient_dashboard')
    else:
        # Pre-fill the doctor if passed via URL (e.g., from the Doctor List page)
        doctor_id = request.GET.get('doctor')
        initial_data = {'doctor': doctor_id} if doctor_id else {}
        form = AppointmentForm(initial=initial_data)

    return render(request, 'appointments/book.html', {'form': form})


@login_required
def appointment_history(request):
    if not request.user.is_patient:
        return redirect('home')

    patient = Patient.objects.get(user=request.user)

    # FIXED: Changed to '-appointment_date' and '-appointment_time'
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-appointment_time')

    # Handle Status Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    return render(request, 'appointments/history.html', {
        'appointments': appointments,
        'status_filter': status_filter
    })


# --- STATUS UPDATE VIEWS (Shared by Doctors and Patients) ---

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    # Security check: Ensure the user owns this appointment
    is_owner = (request.user.is_patient and appointment.patient.user == request.user)
    is_doctor = (request.user.is_doctor and appointment.doctor.user == request.user)

    if is_owner or is_doctor:
        appointment.status = 'Cancelled'
        appointment.save()
        if request.user.is_doctor:
            create_notification(appointment.patient.user,f"Dr. {appointment.doctor.user.last_name} has CANCELLED your appointment on {appointment.date}.")
        elif request.user.is_patient:
            create_notification(appointment.doctor.user,
                                f"{appointment.patient.user.get_full_name()} has CANCELLED their appointment on {appointment.date}.")
        messages.success(request, "Appointment cancelled successfully.")

    # Redirect back to the correct dashboard
    if request.user.is_doctor:
        return redirect('doctor_dashboard')
    return redirect('patient_dashboard')


@login_required
def book_appointment(request):
    # 1. Try to get doctor ID from the URL (?doctor=6)
    doctor_id = request.GET.get('doctor')

    # If no ID is found, don't just redirect—show an error so we know!
    if not doctor_id:
        messages.error(request, "No doctor was selected. Please choose a doctor first.")
        return redirect('doctor_list')  # Redirect to list instead of home

    doctor = get_object_or_404(Doctor, id=doctor_id)

    # 2. Ensure the patient profile exists (The "Welcome Mat")
    from patients.models import Patient
    patient_profile, created = Patient.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient_profile
            appointment.doctor = doctor
            appointment.save()
            messages.success(request, "Appointment requested successfully!")
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm(initial={'doctor': doctor})

    return render(request, 'appointments/book.html', {
        'form': form,
        'doctor': doctor
    })


@login_required
def approve_appointment(request, pk):
    print(f"DEBUG: User: {request.user.username}")
    print(f"DEBUG: is_doctor: {request.user.is_doctor}")
    print(f"DEBUG: is_superuser: {request.user.is_superuser}")
    # 1. LOGICAL FIX: Allow Doctors OR Admins (Superusers)
    if not (request.user.is_doctor or request.user.is_superuser):
        messages.error(request, "Access Denied: You do not have permission to approve appointments.")
        return redirect('home')

    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Approved'
    appointment.save()

    messages.success(request, f"Appointment for {appointment.patient.user.get_full_name()} approved.")

    # 2. Redirect back to where you came from
    if request.user.is_superuser:
        return redirect('admin_dashboard')  # Or whatever your admin dashboard name is
    return redirect('doctor_dashboard')


@login_required
def reject_appointment(request, pk):
    if not request.user.is_doctor:
        return redirect('home')

    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Rejected'
    appointment.save()

    messages.warning(request, "Appointment has been rejected.")
    return redirect('doctor_dashboard')


@login_required
def reject_appointment(request, pk):
    # Only allow doctors or admins
    if not (request.user.is_doctor or request.user.is_superuser):
        return redirect('home')

    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Rejected'
    appointment.save()

    messages.warning(request, f"Appointment for {appointment.patient.user.get_full_name()} has been rejected.")

    # Redirect back to the dashboard
    if request.user.is_doctor:
        return redirect('doctor_dashboard')
    return redirect('admin_panel')