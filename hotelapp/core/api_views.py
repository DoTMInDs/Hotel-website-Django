from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import date

from .models import (
    Hotel, Room, Booking, Guest, Reservation, Service,
    Amenity, Rating, Staff, Review, Manager, Lead,
    HotelPaystackSubaccount, OurRoomsImage, CustomUser
)
from .serializers import (
    HotelListSerializer, HotelDetailSerializer, RoomListSerializer,
    RoomDetailSerializer, BookingSerializer, GuestSerializer,
    ReservationSerializer, ServiceSerializer, AmenitySerializer,
    RatingSerializer, StaffSerializer, ReviewSerializer,
    ManagerSerializer, LeadSerializer, UserSerializer,
    UserRegistrationSerializer, ProfileModelSerializer,
    RoomAvailabilitySerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, ChangePasswordSerializer,
    OurRoomsImageSerializer
)

# Define User model
User = CustomUser


# Authentication Views
class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """Get and update user profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        profile_data = None
        
        # Get profile if exists
        if hasattr(request.user, 'profilemodel'):
            from account.models import ProfileModel
            from .serializers import ProfileModelSerializer
            profile_serializer = ProfileModelSerializer(request.user.profilemodel, context={'request': request})
            profile_data = profile_serializer.data
        
        return Response({
            'user': serializer.data,
            'profile': profile_data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Update user profile (full update)"""
        from account.models import ProfileModel
        from .serializers import ProfileModelSerializer
        
        # Get or create profile
        profile, created = ProfileModel.objects.get_or_create(user=request.user)
        
        # Update user fields if provided
        user_fields = ['first_name', 'last_name', 'email']
        for field in user_fields:
            if field in request.data:
                setattr(request.user, field, request.data[field])
        request.user.save()
        
        # Update profile
        serializer = ProfileModelSerializer(profile, data=request.data, partial=False, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'user': UserSerializer(request.user).data,
                'profile': serializer.data,
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Update user profile (partial update)"""
        from account.models import ProfileModel
        from .serializers import ProfileModelSerializer
        
        # Get or create profile
        profile, created = ProfileModel.objects.get_or_create(user=request.user)
        
        # Update user fields if provided
        user_fields = ['first_name', 'last_name', 'email']
        for field in user_fields:
            if field in request.data:
                setattr(request.user, field, request.data[field])
        request.user.save()
        
        # Update profile
        serializer = ProfileModelSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'user': UserSerializer(request.user).data,
                'profile': serializer.data,
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """Request password reset - sends email with reset link"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL (adjust frontend URL as needed)
            reset_url = f"{request.scheme}://{request.get_host()}/api/auth/password-reset-confirm/{uid}/{token}/"
            
            # For Flutter app, you might want a deep link:
            # reset_url = f"yourapp://reset-password?uid={uid}&token={token}"
            
            # Send email
            try:
                send_mail(
                    subject='Password Reset Request',
                    message=f'Hi {user.username},\n\nClick the link below to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email.\n\nThis link expires in 24 hours.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Password reset email sent successfully',
                    'uid': uid,  # Include for testing/Flutter deep linking
                    'token': token  # Include for testing/Flutter deep linking
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'Failed to send email. Please try again later.',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Confirm password reset with token and set new password"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Password reset successful. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """Change password when logged in"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Hotel ViewSet
class HotelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Hotel CRUD operations
    
    Endpoints:
    - GET /api/hotels/ - List all hotels
    - POST /api/hotels/ - Create hotel (admin only)
    - GET /api/hotels/{id}/ - Get hotel details
    - PUT/PATCH /api/hotels/{id}/ - Update hotel (admin only)
    - DELETE /api/hotels/{id}/ - Delete hotel (admin only)
    - GET /api/hotels/{id}/rooms/ - Get hotel rooms
    - GET /api/hotels/{id}/available-rooms/ - Get available rooms
    """
    queryset = Hotel.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region', 'has_payment_setup']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HotelListSerializer
        return HotelDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """Get all rooms for a specific hotel"""
        hotel = self.get_object()
        rooms = hotel.rooms.all()
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def available_rooms(self, request, pk=None):
        """Get available rooms for a specific hotel"""
        hotel = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        available_rooms = hotel.rooms.filter(status='Available')
        
        # Filter by date availability if dates provided
        if check_in and check_out:
            # Exclude rooms with overlapping reservations
            from django.db.models import Q
            overlapping = Reservation.objects.filter(
                Q(check_in_date__lt=check_out) & Q(check_out_date__gt=check_in),
                status__in=['Pending', 'Confirmed', 'Checked In']
            ).values_list('room_id', flat=True)
            
            available_rooms = available_rooms.exclude(id__in=overlapping)
        
        serializer = RoomListSerializer(available_rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get hotel statistics"""
        hotel = self.get_object()
        
        stats = {
            'total_rooms': hotel.rooms.count(),
            'available_rooms': hotel.rooms.filter(status='Available').count(),
            'occupied_rooms': hotel.rooms.filter(status='Occupied').count(),
            'total_bookings': Booking.objects.filter(room__hotel=hotel).count(),
            'total_reservations': Reservation.objects.filter(room__hotel=hotel).count(),
            'total_reviews': Review.objects.filter(reservation__room__hotel=hotel).count(),
            'average_rating': Review.objects.filter(
                reservation__room__hotel=hotel
            ).aggregate(avg=Avg('rating__star'))['avg'] or 0,
        }
        
        return Response(stats)


# Room ViewSet
class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Room CRUD operations
    
    Endpoints:
    - GET /api/rooms/ - List all rooms
    - POST /api/rooms/ - Create room (admin only)
    - GET /api/rooms/{id}/ - Get room details
    - PUT/PATCH /api/rooms/{id}/ - Update room (admin only)
    - DELETE /api/rooms/{id}/ - Delete room (admin only)
    - GET /api/rooms/available/ - Get available rooms
    - POST /api/rooms/{id}/check-availability/ - Check room availability
    """
    queryset = Room.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hotel', 'room_type', 'bed_type', 'status', 'max_guests']
    search_fields = ['room_number', 'hotel__name']
    ordering_fields = ['price', 'created_at', 'room_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoomListSerializer
        return RoomDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available rooms"""
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        available_rooms = Room.objects.filter(status='Available')
        
        if check_in and check_out:
            overlapping = Reservation.objects.filter(
                Q(check_in_date__lt=check_out) & Q(check_out_date__gt=check_in),
                status__in=['Pending', 'Confirmed', 'Checked In']
            ).values_list('room_id', flat=True)
            
            available_rooms = available_rooms.exclude(id__in=overlapping)
        
        serializer = RoomListSerializer(available_rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_availability(self, request, pk=None):
        """Check if room is available for specific dates"""
        room = self.get_object()
        serializer = RoomAvailabilitySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        check_in = serializer.validated_data['check_in_date']
        check_out = serializer.validated_data['check_out_date']
        
        # Check if room has status Available
        if room.status != 'Available':
            return Response({
                'available': False,
                'message': f'Room is currently {room.get_status_display()}'
            })
        
        # Check for overlapping reservations
        overlapping = Reservation.objects.filter(
            room=room,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
            status__in=['Pending', 'Confirmed', 'Checked In']
        ).exists()
        
        if overlapping:
            return Response({
                'available': False,
                'message': 'Room is already booked for the selected dates'
            })
        
        return Response({
            'available': True,
            'message': 'Room is available for booking',
            'price_per_night': room.price,
            'total_nights': (check_out - check_in).days,
            'total_price': float(room.price) * (check_out - check_in).days
        })


# Guest ViewSet
class GuestViewSet(viewsets.ModelViewSet):
    """ViewSet for Guest management"""
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's guest profile"""
        try:
            guest = Guest.objects.get(user=request.user)
            serializer = self.get_serializer(guest)
            return Response(serializer.data)
        except Guest.DoesNotExist:
            return Response({
                'error': 'Guest profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Get all bookings for a guest"""
        guest = self.get_object()
        bookings = guest.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reservations(self, request, pk=None):
        """Get all reservations for a guest"""
        guest = self.get_object()
        reservations = guest.reservations.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)


# Booking ViewSet
class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Booking (online bookings with payment)
    
    Endpoints:
    - GET /api/bookings/ - List bookings
    - POST /api/bookings/ - Create booking
    - GET /api/bookings/{id}/ - Get booking details
    - PUT/PATCH /api/bookings/{id}/ - Update booking
    - DELETE /api/bookings/{id}/ - Cancel booking
    - GET /api/bookings/my-bookings/ - Get current user's bookings
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_paid', 'room', 'guest']
    ordering_fields = ['created_at', 'check_in_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        # Regular users only see their bookings
        return Booking.objects.filter(guest__user=user)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get current user's bookings"""
        try:
            guest = Guest.objects.get(user=request.user)
            bookings = Booking.objects.filter(guest=guest)
            serializer = self.get_serializer(bookings, many=True)
            return Response(serializer.data)
        except Guest.DoesNotExist:
            return Response([])
    
    def perform_create(self, serializer):
        """Auto-assign current user's guest profile"""
        guest, created = Guest.objects.get_or_create(
            user=self.request.user,
            defaults={
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email
            }
        )
        serializer.save(guest=guest)


# Reservation ViewSet
class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for Reservation management"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'room', 'guest', 'check_in_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['check_in_date', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Staff see all reservations
            return Reservation.objects.all()
        # Guests only see their reservations
        return Reservation.objects.filter(guest__user=user)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming reservations"""
        queryset = self.get_queryset().filter(
            check_in_date__gte=date.today(),
            status__in=['Pending', 'Confirmed']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past reservations"""
        queryset = self.get_queryset().filter(
            status__in=['Checked Out', 'Cancelled', 'No Show']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Service ViewSet
class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Service management"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]


# Amenity ViewSet
class AmenityViewSet(viewsets.ModelViewSet):
    """ViewSet for Amenity management"""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]


# Rating ViewSet
class RatingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Rating (read-only)"""
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]


# Staff ViewSet
class StaffViewSet(viewsets.ModelViewSet):
    """ViewSet for Staff management"""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['hotel', 'position', 'department', 'is_active']
    search_fields = ['full_name', 'email', 'phone_number']


# Review ViewSet
class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review management"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating']
    ordering_fields = ['created_at', 'rating__star']
    
    @action(detail=False, methods=['get'])
    def hotel_reviews(self, request):
        """Get reviews for a specific hotel"""
        hotel_id = request.query_params.get('hotel_id')
        if not hotel_id:
            return Response({
                'error': 'hotel_id parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reviews = Review.objects.filter(
            reservation__room__hotel_id=hotel_id
        )
        serializer = self.get_serializer(reviews, many=True)
        
        # Calculate average rating
        avg_rating = reviews.aggregate(avg=Avg('rating__star'))['avg'] or 0
        
        return Response({
            'reviews': serializer.data,
            'average_rating': round(avg_rating, 1),
            'total_reviews': reviews.count()
        })


# Manager ViewSet
class ManagerViewSet(viewsets.ModelViewSet):
    """ViewSet for Manager management"""
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated]


# Lead ViewSet
class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet for Lead management"""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


# OurRoomsImage ViewSet
class OurRoomsImageViewSet(viewsets.ModelViewSet):
    """ViewSet for Room Images (additional images)"""
    queryset = OurRoomsImage.objects.all()
    serializer_class = OurRoomsImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room']
    ordering_fields = ['id']
    ordering = ['id']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


# Search and Filter Views
@api_view(['GET'])
@permission_classes([AllowAny])
def search_hotels(request):
    """
    Search hotels by various criteria
    Query params: q (search term), region, min_price, max_price
    """
    query = request.GET.get('q', '')
    region = request.GET.get('region', '')
    
    hotels = Hotel.objects.all()
    
    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )
    
    if region:
        hotels = hotels.filter(region=region)
    
    serializer = HotelListSerializer(hotels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_rooms(request):
    """
    Search rooms by various criteria
    Query params: hotel, room_type, min_price, max_price, max_guests, check_in, check_out
    """
    hotel_id = request.GET.get('hotel')
    room_type = request.GET.get('room_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    max_guests = request.GET.get('max_guests')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    rooms = Room.objects.filter(status='Available')
    
    if hotel_id:
        rooms = rooms.filter(hotel_id=hotel_id)
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if min_price:
        rooms = rooms.filter(price__gte=min_price)
    if max_price:
        rooms = rooms.filter(price__lte=max_price)
    if max_guests:
        rooms = rooms.filter(max_guests__gte=max_guests)
    
    # Filter by date availability
    if check_in and check_out:
        overlapping = Reservation.objects.filter(
            Q(check_in_date__lt=check_out) & Q(check_out_date__gt=check_in),
            status__in=['Pending', 'Confirmed', 'Checked In']
        ).values_list('room_id', flat=True)
        
        rooms = rooms.exclude(id__in=overlapping)
    
    serializer = RoomListSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint with available endpoints"""
    return Response({
        'message': 'Welcome to Hotel Booking API',
        'version': '1.0',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'profile': '/api/auth/profile/',
            },
            'hotels': '/api/hotels/',
            'rooms': '/api/rooms/',
            'room-images': '/api/room-images/',
            'bookings': '/api/bookings/',
            'reservations': '/api/reservations/',
            'guests': '/api/guests/',
            'services': '/api/services/',
            'amenities': '/api/amenities/',
            'reviews': '/api/reviews/',
            'leads': '/api/leads/',
            'search': {
                'hotels': '/api/search/hotels/',
                'rooms': '/api/search/rooms/',
            },
            'documentation': '/api/docs/',
        }
    })
