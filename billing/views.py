from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Invoice

@login_required
def billing_history(request):
    # Get all invoices related to the logged-in user's appointments
    invoices = Invoice.objects.filter(appointment__patient__user=request.user)
    return render(request, 'billing/history.html', {'invoices': invoices})