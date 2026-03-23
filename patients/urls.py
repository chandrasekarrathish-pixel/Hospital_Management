from django.urls import path
from . import views

urlpatterns = [
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-records/', views.my_records, name='my_records'),
    path('medical-history/', views.my_records, name='medical_history'),
]