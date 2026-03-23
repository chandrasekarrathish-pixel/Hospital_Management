from django.urls import path
from . import views
from core import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
]