from django.urls import path
from . import views

urlpatterns = [
    path('my-patients/', views.my_patients, name='my_patients'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('list/', views.doctor_list, name='doctor_list'),
]