from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('history/', views.appointment_history, name='appointment_history'),
    path('cancel/<int:pk>/', views.cancel_appointment, name='cancel_appointment'),
    path('approve/<int:pk>/', views.approve_appointment, name='approve_appointment'),
    path('reject/<int:pk>/', views.reject_appointment, name='reject_appointment'),
]