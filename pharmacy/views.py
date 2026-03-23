from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Medicine, PharmacyInventory
from .forms import MedicineForm, InventoryForm
from django.utils import timezone
from django.db.models import Q


# --- Permission Check ---
def is_pharmacy_worker(user):
    in_group = user.groups.filter(name='Pharmacy_Worker').exists()
    is_admin = user.is_superuser or getattr(user, 'is_admin', False)
    return in_group or is_admin


# --- Pharmacy Worker Dashboard ---
@login_required
def pharmacy_worker_dashboard(request):
    # 1. SECURITY CHECK
    is_worker = request.user.groups.filter(name='Pharmacy_Worker').exists()
    is_admin = request.user.is_superuser

    if not (is_worker or is_admin):
        return redirect('home')

    # 2. DATA RETRIEVAL
    today = timezone.now().date()
    search_query = request.GET.get('search', '').strip()

    inventory = PharmacyInventory.objects.select_related('medicine').all()
    if search_query:
        # Searches for Medicine Name OR the Inventory ID
        inventory = inventory.filter(
            Q(medicine__name__icontains=search_query) |
            Q(id__icontains=search_query)
        )

    inventory = inventory.order_by('medicine__name')

    # 3. POST LOGIC
    if request.method == "POST" and 'sell_id' in request.POST:
        item = get_object_or_404(PharmacyInventory, id=request.POST.get('sell_id'))
        try:
            qty = int(request.POST.get('quantity', 1))
            if item.stock_quantity >= qty:
                item.stock_quantity -= qty
                item.save()
                messages.success(request, f"Billed {qty} units of {item.medicine.name}")
            else:
                messages.error(request, "Insufficient stock!")
        except ValueError:
            pass
        return redirect('pharmacy_worker_dashboard')

    return render(request, 'pharmacy/worker_dashboard.html', {
        'inventory': inventory,
        'today': today,
        'search_query': search_query
    })


# --- Inventory List (Admin Master View) ---
@login_required
def inventory_list(request):
    if not (request.user.is_superuser or getattr(request.user, 'is_admin', False)):
        messages.error(request, "Access restricted to Administrators.")
        return redirect('home')

    inventory = PharmacyInventory.objects.select_related('medicine').all().order_by('medicine__name')
    today = timezone.now().date()

    search_query = request.GET.get('search', '')
    if search_query:
        inventory = inventory.filter(medicine__name__icontains=search_query)

    stock_filter = request.GET.get('filter', '')
    if stock_filter == 'low':
        inventory = inventory.filter(stock_quantity__lt=20, stock_quantity__gt=0)
    elif stock_filter == 'out':
        inventory = inventory.filter(stock_quantity=0)
    elif stock_filter == 'expired':
        inventory = inventory.filter(expiry_date__lt=today)

    return render(request, 'pharmacy/inventory.html', {
        'inventory': inventory,
        'today': today,
        'search_query': search_query,
        'stock_filter': stock_filter
    })


# --- Add/Update views ---
@login_required
@user_passes_test(is_pharmacy_worker, login_url='home')
def add_medicine(request):
    if request.method == 'POST':
        med_form = MedicineForm(request.POST)
        inv_form = InventoryForm(request.POST)
        if med_form.is_valid() and inv_form.is_valid():
            medicine = med_form.save()
            inventory = inv_form.save(commit=False)
            inventory.medicine = medicine
            inventory.save()
            messages.success(request, f"{medicine.name} added successfully!")
            return redirect('pharmacy_worker_dashboard')
    else:
        med_form = MedicineForm()
        inv_form = InventoryForm()
    return render(request, 'dashboard/add_medicine.html', {
        'med_form': med_form,
        'inv_form': inv_form
    })


@login_required
@user_passes_test(is_pharmacy_worker, login_url='home')
def update_stock(request, inventory_id):
    inventory = get_object_or_404(PharmacyInventory, id=inventory_id)
    if request.method == 'POST':
        inv_form = InventoryForm(request.POST, instance=inventory)
        if inv_form.is_valid():
            inv_form.save()
            messages.success(request, "Stock updated.")
            return redirect('pharmacy_worker_dashboard')
    else:
        inv_form = InventoryForm(instance=inventory)
    return render(request, 'pharmacy/update_stock.html', {'inv_form': inv_form, 'medicine': inventory.medicine})


# pharmacy/views.py

@login_required
def create_bill(request):
    inventory = PharmacyInventory.objects.select_related('medicine').all()

    # If it's a POST, we are finishing the bill and generating an invoice
    if request.method == "POST":
        # Here you would normally save a 'Sale' record to the database
        items_json = request.POST.get('bill_items')  # Sent via JavaScript
        # Process stock reduction here...
        messages.success(request, "Invoice Generated Successfully!")
        return redirect('pharmacy_worker_dashboard')

    return render(request, 'pharmacy/create_bill.html', {
        'inventory': inventory,
    })