from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.billing_history, name='billing_history'),
]