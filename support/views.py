from django.shortcuts import render, redirect
from .models import SupportMessage


def contact_support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        is_emergency = request.POST.get('is_emergency') == 'on'  # Checkbox value

        SupportMessage.objects.create(
            sender_name=name,
            email=email,
            message=message,
            is_emergency=is_emergency
        )
        # Redirect to a simple success page or home
        return redirect('home')

    return render(request, 'support/contact.html')