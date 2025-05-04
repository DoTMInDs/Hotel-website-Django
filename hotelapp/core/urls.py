from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('hotel/', views.hotel, name='hotel'),
    path('hotel/services/<int:pk>/', views.hotel_services, name='hotel-services'),
    path('my_booking/', views.my_booking, name='my_booking'),
    path('hotel_rooms/', views.hotel_rooms, name='hotel-rooms'),
    path('hotel_rooms/room-list/<int:pk>/', views.room_list, name='room-list'),
    path('room_detail/<int:pk>/', views.room_detail, name='room-detail'),
    path('booking/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
]
