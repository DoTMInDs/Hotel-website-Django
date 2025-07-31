from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('sign_up/', views.sign_up, name='sign-up'),
    path('login/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),

    
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='account/password/password_reset.html',
                                                                 email_template_name='account/password/password_reset_email.html'),
                                                                   name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='account/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='account/password/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password/password_reset_complete.html'), name='password_reset_complete'),


    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-hotel-account/', views.manage_hotel_account, name='manage-hotel-account'),
    path('guest/', views.guest, name='guest'),
    path('remove-amenity/<int:amenity_id>/', views.remove_amenity, name='remove-amenity'),
    path('reservation/', views.reservation, name='reservation'),
    path('add-room/', views.add_room, name='add-room'),
    path('services/', views.services, name='services'),
    path('edit_service/<int:pk>/', views.edit_service, name='edit-service'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete-service'),
    path('manage-account/', views.manage_account, name='manage-account'),
    path('add_room_detail/<int:pk>/', views.add_room_detail, name='add-room-detail'),
    path('edit_room/<int:pk>/edit/', views.edit_room, name='edit-room'),
    path('edit_staff/<int:pk>/', views.edit_staff, name='edit-staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete-staff'),
    path('reservation/delete/<int:reservation_id>/', views.delete_reservation, name='delete-reservation'),
    path('reservation/edit/<int:pk>/', views.edit_reservation, name='edit-reservation'),
   
]
