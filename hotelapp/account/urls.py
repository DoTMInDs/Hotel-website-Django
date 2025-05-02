from django.urls import path
from . import views

urlpatterns = [
    path('sign_up/', views.sign_up, name='sign-up'),
    path('login/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('guest/', views.guest, name='guest'),
    path('reservation/', views.reservation, name='reservation'),
    path('add-room/', views.add_room, name='add-room'),
    path('services/', views.services, name='services'),
    path('manage-account/', views.manage_account, name='manage-account'),
    path('add_room_detail/<int:pk>/', views.add_room_detail, name='add-room-detail'),
    path('edit_room/<int:pk>/edit/', views.edit_room, name='edit-room'),
    path('edit_staff/<int:pk>/', views.edit_staff, name='edit-staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete-staff'),
    path('reservation/delete/<int:reservation_id>/', views.delete_reservation, name='delete-reservation'),
    path('reservation/edit/<int:pk>/', views.edit_reservation, name='edit-reservation'),
]
