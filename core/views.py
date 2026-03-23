from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # FIXED: Correct import for messages
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor
from appointments.forms import AppointmentForm
from patients.models import Patient


def home_view(request):
    return render(request, 'core/home.html')


def department_detail(request, dept_name):
    # Filter doctors by department name
    doctors = Doctor.objects.filter(department__name__iexact=dept_name)
    return render(request, 'department_detail.html', {
        'department': dept_name.capitalize(),
        'doctors': doctors
    })


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # 1. Safety Check: Verify the user has a Patient profile
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Access Denied: Doctors and Admins cannot book appointments as patients.")
        return redirect('home')

    patient_profile = request.user.patient

    if request.method == 'POST':
        # Pass the POST data to the form
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient_profile
            # Force the doctor to be the one selected from the card
            appointment.doctor = doctor
            appointment.save()

            messages.success(request, f"Appointment request sent to Dr. {doctor.user.last_name}!")
            return redirect('patient_dashboard')
    else:
        # Pre-fill the hidden doctor field in the form
        form = AppointmentForm(initial={'doctor': doctor})

    return render(request, 'appointments/book.html', {
        'form': form,
        'doctor': doctor
    })