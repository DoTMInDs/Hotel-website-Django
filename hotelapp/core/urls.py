from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('booking/', views.booking, name='booking'),
    path('hotel/', views.hotel, name='hotel'),
    path('detail/<int:pk>/', views.detail, name='detail'),
]
