from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('hotel/', views.hotel, name='hotel'),
    path('my_booking/', views.my_booking, name='my_booking'),
    path('room/', views.room, name='room'),
    path('room_detail/<int:pk>/', views.room_detail, name='room-detail'),
    path('booking/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
]
