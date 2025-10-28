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



    # Staff Dashboard
    # User Management URLs
    path('staff/dashboard', views.staff_dashboard, name='staff_dashboard'),
    path('staff/user-management', views.user_management, name='user_management'),
    path('staff/user-management/<int:user_id>/', views.user_detail, name='user_detail'),
    # path('staff/user-management/create/', views.create_user, name='create_user'),
    # path('staff/user-management/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('staff/user-management/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('staff/user-management/<int:user_id>/toggle-verification/', views.toggle_verification, name='toggle_verification'),
    path('staff/user-management/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    # Staff Management URLs
    path('staff-management/', views.manage_staff, name='manage_staff'),
    path('staff-management/create/', views.create_staff, name='create_staff'),
    path('staff-management/<int:staff_id>/edit/', views.edit_staff_admin, name='edit_staff_admin'),
    path('staff-management/<int:staff_id>/toggle-status/', views.toggle_staff_status, name='toggle_staff_status'),
    path('staff-management/<int:staff_id>/delete/', views.delete_staff_admin, name='delete_staff_admin'),
    
    # Analytics and Bulk Actions
    path('user-analytics/', views.user_analytics, name='user_analytics'),
    path('bulk-user-actions/', views.bulk_user_actions, name='bulk_user_actions'),
    
    # API Endpoints
    path('api/user-stats/', views.get_user_stats, name='get_user_stats'),
    
    # Room Gallery Management URLs
    path('room/<int:room_id>/gallery/', views.room_gallery_management, name='room-gallery-management'),
    path('room/<int:room_id>/gallery/upload/', views.upload_room_image, name='upload-room-image'),
    path('room/<int:room_id>/gallery/<int:image_id>/delete/', views.delete_room_image, name='delete-room-image'),
   
]
