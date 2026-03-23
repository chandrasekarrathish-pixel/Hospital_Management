from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import PatientSignUpForm
from patients.models import Patient

def register_choice(request):
    return render(request, 'accounts/register_choice.html')


def register_view(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # ADD THIS LINE:
            Patient.objects.create(user=user)

            # CRITICAL: Create the Patient profile linked to this User
            Patient.objects.create(user=user)

            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientSignUpForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # --- Role-Based Redirect Logic ---
            if user.is_admin or user.is_superuser:
                return redirect('admin_dashboard')
            elif user.is_doctor:
                return redirect('doctor_dashboard')
            elif user.is_patient:
                return redirect('patient_dashboard')
            else:
                return redirect('home')  # Fallback
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')