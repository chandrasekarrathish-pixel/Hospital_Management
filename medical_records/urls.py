from django.urls import path
from . import views

urlpatterns = [
    path('upload-lab/<int:patient_id>/', views.upload_lab_report, name='upload_lab_report'),
    path('prescription/download/<int:rx_id>/', views.download_prescription, name='download_prescription'),
]