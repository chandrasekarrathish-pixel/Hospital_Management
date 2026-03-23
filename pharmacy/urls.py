from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('medicine/add/', views.add_medicine, name='add_medicine'),
    path('stock/update/<int:inventory_id>/', views.update_stock, name='update_stock'),
    path('pharmacy/add/', views.add_medicine, name='admin_add_medicine'),
    path('worker-dashboard/', views.pharmacy_worker_dashboard, name='Pharmacy_Worker_dashboard'),
    path('billing/', views.create_bill, name='create_bill'),
]