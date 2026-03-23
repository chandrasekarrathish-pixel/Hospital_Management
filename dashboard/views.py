from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .utils import create_notification
from .models import Notification
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from pharmacy.models import PharmacyInventory
from pharmacy.forms import InventoryForm
# Combined these to avoid duplicate import errors
from medical_records.models import Prescription, LabReport
from datetime import timedelta
from pharmacy.forms import MedicineForm

def home(request):
    is_pharmacy_worker = False
    if request.user.is_authenticated:
        # We check the group here in Python where it is 100% accurate
        is_pharmacy_worker = request.user.groups.filter(name='Pharmacy_Worker').exists()

    context = {
        'is_pharmacy_worker': is_pharmacy_worker,
        # ... your other home context ...
    }
    return render(request, 'core/index.html', context)


@login_required
def admin_dashboard(request):
    # 1. SECURITY: Only allow Admins/Staff
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')

    # 2. BASIC STATS
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()

    today = timezone.now().date()
    thirty_days_from_now = today + timezone.timedelta(days=30)

    # 3. APPOINTMENT STATS
    appointments_today = Appointment.objects.filter(appointment_date=today).count()
    pending_count = Appointment.objects.filter(status='Pending').count()
    recent_appointments = Appointment.objects.all().order_by('-created_at')[:5]

    # 4. PHARMACY STATS (CRITICAL FIX HERE)
    # We remove .select_related('medicine') to stop the FieldError crash
    # until your migrations are 100% finished.
    low_stock_medicines = PharmacyInventory.objects.filter(stock_quantity__lt=10).count()

    expiring_medicines = PharmacyInventory.objects.filter(
        expiry_date__lte=thirty_days_from_now,
        expiry_date__gte=today
    ).order_by('expiry_date')[:5]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'appointments_today': appointments_today,
        'pending_count': pending_count,
        'recent_appointments': recent_appointments,
        'low_stock_medicines': low_stock_medicines,
        'expiring_medicines': expiring_medicines,
        'today': today,
    }

    return render(request, 'dashboard/admin.html', context)


@login_required
def admin_patient_list(request):
    """View to show all registered patients to the Admin."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')

    patients = Patient.objects.all().order_by('-id')  # Newest patients first

    return render(request, 'dashboard/admin_patient_list.html', {'patients': patients})
@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return redirect('home')

    today = timezone.now().date()

    # We use get_object_or_404 to prevent the 'DoesNotExist' crash
    doctor_profile = get_object_or_404(Doctor, user=request.user)

    context = {
        'doctor': doctor_profile,

        # FIXED: Use 'appointment_date' and filter for 'Approved' status
        'today_appointments': Appointment.objects.filter(
            doctor=doctor_profile,
            appointment_date=today,
            status='Approved'
        ),

        # This keeps your red notification bubble working
        'pending_requests': Appointment.objects.filter(
            doctor=doctor_profile,
            status='Pending'
        ).count(),

        # This sends the list to your "Pending Requests" table
        'pending_appointments': Appointment.objects.filter(
            doctor=doctor_profile,
            status='Pending'
        ),
    }
    return render(request, 'dashboard/doctor.html', context)


@login_required

def patient_dashboard(request):
    if request.user.groups.filter(name='Pharmacy_Worker').exists():
        return redirect('pharmacy_worker_dashboard')


    if not request.user.is_patient:
        return redirect('home')

    # Use get_object_or_404 for better error handling
    patient_profile = Patient.objects.get(user=request.user)

    # Get current date
    today = timezone.now().date()

    context = {
        'patient': patient_profile,
        # LOGICAL FIX: Filter for appointments where date is today or later (__gte)
        'my_appointments': Appointment.objects.filter(
            patient=patient_profile,
            appointment_date__gte=today
        ).order_by('appointment_date', 'appointment_time'),
    }
    return render(request, 'dashboard/patient.html', context)

@login_required
def mark_notifications_read(request):
    # Mark all unread notifications for this user as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    # Redirect back to the page they were just on
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def admin_patient_detail(request, patient_id):
    """View to show a specific patient's full medical history to the Admin."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')

    # 1. Fetch the specific patient or 404
    patient = get_object_or_404(Patient, id=patient_id)

    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_issued')
    lab_reports = LabReport.objects.filter(patient=patient).order_by('-generated_on')

    # 4. Package it all up (CRITICAL: Added lab_reports here)
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'lab_reports': lab_reports,  # <--- THIS WAS MISSING
    }
    return render(request, 'dashboard/admin_patient_detail.html', context)

# dashboard/views.py

@login_required
def admin_doctor_list(request):
    """View to show all registered doctors to the Admin."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')

    doctors = Doctor.objects.all().order_by('user__first_name')
    return render(request, 'dashboard/admin_doctor_list.html', {'doctors': doctors})




@login_required
def admin_appointment_list(request):
    """View for Admin to see all appointment requests and their status."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')
    query = request.GET.get('search', '').strip()
    today = timezone.now().date()
    appointments = Appointment.objects.filter(appointment_date__gte=today)
    if query:
        appointments = appointments.filter(
            Q(patient__user__first_name__icontains=query) |
            Q(patient__user__last_name__icontains=query) |
            Q(patient__contact_number__icontains=query)
        )
    # Get all appointments, newest first
    appointments = appointments.order_by('-appointment_date', '-appointment_time')
    context = {
        'appointments': appointments,
        'search_query': query,  # This keeps the text in the search box
    }

    return render(request, 'dashboard/admin_appointment_list.html', context)




@login_required
def approve_appointment(request, appointment_id):
    """View for Admin to approve a pending appointment."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Approved'
    appointment.save()

    # Optional: Send a notification to the patient
    create_notification(appointment.patient.user,
                        f"Your appointment with Dr. {appointment.doctor.user.last_name} on {appointment.appointment_date} has been approved.")

    messages.success(request, f"Appointment for {appointment.patient.user.get_full_name()} approved successfully.")
    return redirect('admin_appointment_list')

# dashboard/views.py

@login_required
def admin_pharmacy_list(request):
    """View to show full Pharmacy Inventory to the Admin."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')

    inventory = PharmacyInventory.objects.all().order_by('medicine')
    today = timezone.now().date()
    warning_date = today + timedelta(days=30)
    context = {
        'inventory': inventory,
        'today': today,
        'warning_date': warning_date,
    }
    return render(request, 'dashboard/admin_pharmacy_list.html', context)


@login_required
def add_medicine(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')


    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New medicine added successfully!")
            return redirect('admin_pharmacy_list')
        else:
            print(form.errors)
    else:
        form = MedicineForm()

    return render(request, 'dashboard/add_medicine.html', {'form': form})


@login_required
def pharmacy_worker_dashboard(request):
    # 1. Security Check: Only Workers or Admins
    is_worker = request.user.groups.filter(name='Pharmacy_Worker').exists()
    is_admin = request.user.is_superuser or request.user.is_staff

    if not (is_worker or is_admin):
        messages.error(request, "Access Denied: Pharmacy Staff only.")
        return redirect('home')

    today = timezone.now().date()
    # Fetch inventory
    inventory = PharmacyInventory.objects.all().order_by('medicine')

    # 2. Quick Billing Logic (POST request)
    if request.method == "POST" and 'sell_id' in request.POST:
        item = get_object_or_404(PharmacyInventory, id=request.POST.get('sell_id'))
        try:
            qty = int(request.POST.get('quantity', 1))
            if qty > 0 and item.stock_quantity >= qty:
                item.stock_quantity -= qty
                item.save()
                messages.success(request, f"Billed {qty} units of {item.medicine}")
            else:
                messages.error(request, "Insufficient stock!")
        except ValueError:
            messages.error(request, "Invalid quantity.")
        return redirect('pharmacy_worker_dashboard')

    context = {
        'inventory': inventory,
        'today': today,
    }
    # Note: Pointing to the pharmacy folder for the template
    return render(request, 'pharmacy/worker_dashboard.html', context)