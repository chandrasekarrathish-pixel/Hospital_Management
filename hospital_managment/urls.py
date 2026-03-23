"""
URL configuration for hospital_managment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from doctors.views import doctor_list
from django.conf import settings
from django.conf.urls.static import static
from core import views
from core import views as core_views
from dashboard import views as dashboard_views
from pharmacy import views as pharmacy_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),

    # Including App-Specific URLs

    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('billing/', include('billing.urls')),
    path('support/', include('support.urls')),
    path('department/<str:dept_name>/', views.department_detail, name='department_detail'),
    path('', include('core.urls')), # This routes the base URL to our new homepage!
    path('dashboard/pharmacy-worker/', pharmacy_views.pharmacy_worker_dashboard, name='pharmacy_worker_dashboard'),
    path('dashboard/', include('dashboard.urls')),
    path('appointments/', include('appointments.urls')),
    path('records/', include('medical_records.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('admin-panel/patients/', dashboard_views.admin_patient_list, name='admin_patient_list'),
    path('admin-panel/', dashboard_views.admin_dashboard, name='admin_panel'),
    path('admin-panel/patient/<int:patient_id>/', dashboard_views.admin_patient_detail, name='admin_patient_detail'),
    path('admin-panel/doctors/', dashboard_views.admin_doctor_list, name='admin_doctor_list'),
    path('admin-panel/appointments/', dashboard_views.admin_appointment_list, name='admin_appointment_list'),
    path('admin-panel/approve-appointment/<int:appointment_id>/', dashboard_views.approve_appointment, name='approve_appointment'),
    path('admin-panel/pharmacy/', dashboard_views.admin_pharmacy_list, name='admin_pharmacy_list'),
    path('admin-panel/pharmacy/add/', pharmacy_views.add_medicine, name='add_medicine'),
    path('pharmacy/add/', pharmacy_views.add_medicine, name='admin_add_medicine'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)