from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    manufacturer = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name

class PharmacyInventory(models.Model):
    # CHANGE: medicine must be a ForeignKey to link to the Medicine class
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='inventory')
    stock_quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Now this works because medicine is an object, not just text
        return f"{self.medicine.name} - Stock: {self.stock_quantity}"