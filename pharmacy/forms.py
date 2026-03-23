from django import forms
from .models import PharmacyInventory, Medicine


class MedicineForm(forms.ModelForm):
    price = forms.DecimalField(
        initial='0.00',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )
    class Meta:
        model = Medicine  # CHANGE: Point this to your Medicine model
        fields = ['name', 'description', 'price', 'manufacturer']

        widgets = {
            # 2. Match the widgets to the fields listed above
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Paracetamol 500mg'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medicine description...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manufacturer name'
            }),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = PharmacyInventory
        fields = ['stock_quantity', 'expiry_date']
        widgets = {

            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }