from django.urls import path
from . import views

urlpatterns = [
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor-panel/', views.doctor_dashboard, name='doctor_dashboard'),
    path('my-portal/', views.patient_dashboard, name='patient_dashboard'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('pharmacy-worker/', views.pharmacy_worker_dashboard, name='pharmacy_worker_dashboard'),
]