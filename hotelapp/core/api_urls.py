from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .api_views import (
    HotelViewSet, RoomViewSet, BookingViewSet, GuestViewSet,
    ReservationViewSet, ServiceViewSet, AmenityViewSet,
    RatingViewSet, StaffViewSet, ReviewViewSet, ManagerViewSet,
    LeadViewSet, RegisterView, LoginView, LogoutView,
    UserProfileView, PasswordResetRequestView, PasswordResetConfirmView,
    ChangePasswordView, search_hotels, search_rooms, api_root
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'guests', GuestViewSet, basename='guest')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'amenities', AmenityViewSet, basename='amenity')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'leads', LeadViewSet, basename='lead')

# Define URL patterns
urlpatterns = [
    # API Root
    path('', api_root, name='api-root'),
    
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Password management endpoints
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Search endpoints
    path('search/hotels/', search_hotels, name='search-hotels'),
    path('search/rooms/', search_rooms, name='search-rooms'),
    
    # Include router URLs
    path('', include(router.urls)),
]
