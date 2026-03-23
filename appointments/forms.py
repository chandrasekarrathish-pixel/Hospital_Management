from django import forms
from .models import Appointment
from doctors.models import Doctor
from datetime import date, timedelta, datetime


# Generate time slots dynamically (9 AM to 5 PM, every 30 mins)
def get_time_slots():
    slots = []
    current_time = datetime.strptime('09:00', '%H:%M')
    end_time = datetime.strptime('17:00', '%H:%M')
    while current_time <= end_time:
        time_str = current_time.strftime('%H:%M')
        # (Value saved to DB, Label shown to user)
        slots.append((time_str, current_time.strftime('%I:%M %p')))
        current_time += timedelta(minutes=30)
    return slots


class AppointmentForm(forms.ModelForm):
    # We keep 'doctor' in the fields but we will hide it in the HTML
    # or pass it from the view to keep the form valid.
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        widget=forms.HiddenInput(),  # Changed to HiddenInput
        required=False
    )

    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control border-start-0',
            'min': date.today().isoformat()
        })
    )

    appointment_time = forms.ChoiceField(
        choices=get_time_slots(),
        widget=forms.Select(attrs={'class': 'form-select border-start-0'})
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'symptoms']
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your symptoms (e.g. Fever, Headache)...'
            }),
        }

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date and appointment_date < date.today():
            raise forms.ValidationError("You cannot book an appointment in the past.")
        return appointment_date