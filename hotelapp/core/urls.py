from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('hotel/', views.hotel, name='hotel'),
    path('booking/', views.booking, name='booking'),
    path('room/', views.room, name='room'),
    path('detail/<int:pk>/', views.detail, name='detail'),
]
