from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Hotel, Room, Booking, Guest, Reservation, Service, 
    Amenity, Rating, Staff, Review, Manager, Lead,
    HotelPaystackSubaccount, OurRoomsImage
)
from account.models import ProfileModel

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model"""
    guest_id = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'is_verified', 'guest_id', 'created_at']
        read_only_fields = ['id', 'created_at', 'guest_id']
    
    def get_guest_id(self, obj):
        """Get the associated guest ID if it exists"""
        if hasattr(obj, 'guest_profile') and obj.guest_profile:
            return obj.guest_profile.id
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'user_type']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with token"""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link")
        
        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired reset link")
        
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password when logged in"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        return data


class ProfileModelSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    user = UserSerializer(read_only=True)
    profile_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfileModel
        fields = ['id', 'user', 'first_name', 'last_name', 'profile', 'profile_url',
                  'phone', 'email', 'gender', 'nationality', 'address']
        read_only_fields = ['id', 'user']
    
    def get_profile_url(self, obj):
        """Get full URL for profile image"""
        if obj.profile:
            request = self.context.get('request')
            if hasattr(obj.profile, 'url'):
                # For CloudinaryField or similar
                return obj.profile.url
            elif request:
                # For regular ImageField
                return request.build_absolute_uri(obj.profile.url)
        return None
        

class RatingSerializer(serializers.ModelSerializer):
    """Serializer for Rating model"""
    class Meta:
        model = Rating
        fields = ['id', 'star']


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for Amenity model"""
    class Meta:
        model = Amenity
        fields = ['id', 'amenity_name']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'category', 'category_display', 
                  'is_available', 'price', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class HotelPaystackSubaccountSerializer(serializers.ModelSerializer):
    """Serializer for Hotel Paystack Subaccount"""
    hotel_commission_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = HotelPaystackSubaccount
        fields = ['id', 'subaccount_code', 'business_name', 'settlement_bank', 
                  'account_number', 'percentage_charge', 'hotel_commission_percentage',
                  'is_active', 'last_settlement_date', 'total_payments_received', 
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'total_payments_received']


class HotelListSerializer(serializers.ModelSerializer):
    """Simplified serializer for hotel list view"""
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    amenities_count = serializers.SerializerMethodField()
    rooms_count = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    hotel_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'phone_number', 'email', 'location', 
                  'region', 'region_display', 'logo', 'logo_url', 'hotel_image', 'hotel_image_url',
                  'amenities_count', 'rooms_count', 'has_payment_setup', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_amenities_count(self, obj):
        return obj.amenities.count()
    
    def get_rooms_count(self, obj):
        return obj.rooms.count()
    
    def get_logo_url(self, obj):
        """Get full URL for hotel logo"""
        if obj.logo:
            return obj.logo.url if hasattr(obj.logo, 'url') else str(obj.logo)
        return None
    
    def get_hotel_image_url(self, obj):
        """Get full URL for hotel image"""
        if obj.hotel_image:
            return obj.hotel_image.url if hasattr(obj.hotel_image, 'url') else str(obj.hotel_image)
        return None


class HotelDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single hotel view"""
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    paystack_subaccount = HotelPaystackSubaccountSerializer(read_only=True)
    logo_url = serializers.SerializerMethodField()
    hotel_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'phone_number', 'email', 'location', 'description',
                  'region', 'region_display', 'logo', 'logo_url', 'hotel_image', 'hotel_image_url',
                  'amenities', 'services', 'paystack_subaccount', 'has_payment_setup', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_logo_url(self, obj):
        """Get full URL for hotel logo"""
        if obj.logo:
            return obj.logo.url if hasattr(obj.logo, 'url') else str(obj.logo)
        return None
    
    def get_hotel_image_url(self, obj):
        """Get full URL for hotel image"""
        if obj.hotel_image:
            return obj.hotel_image.url if hasattr(obj.hotel_image, 'url') else str(obj.hotel_image)
        return None


class OurRoomsImageSerializer(serializers.ModelSerializer):
    """Serializer for room images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OurRoomsImage
        fields = ['id', 'room', 'image', 'image_url']
    
    def get_image_url(self, obj):
        """Get full URL for room image"""
        if obj.image:
            return obj.image.url if hasattr(obj.image, 'url') else str(obj.image)
        return None


class RoomListSerializer(serializers.ModelSerializer):
    """Simplified serializer for room list view"""
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    bed_type_display = serializers.CharField(source='get_bed_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    star_rating = RatingSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'room_type_display', 
                  'bed_type', 'bed_type_display', 'price', 'status', 'status_display',
                  'max_guests', 'hotel', 'hotel_name', 'star_rating', 'image', 'image_url',
                  'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        """Get full URL for room image"""
        if obj.image:
            return obj.image.url if hasattr(obj.image, 'url') else str(obj.image)
        return None


class RoomDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single room view"""
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    bed_type_display = serializers.CharField(source='get_bed_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    hotel = HotelListSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    star_rating = RatingSerializer(read_only=True)
    additional_images = OurRoomsImageSerializer(source='ourroomsimage_set', many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'room_type_display', 
                  'bed_type', 'bed_type_display', 'price', 'status', 'status_display',
                  'max_guests', 'hotel', 'amenities', 'star_rating', 'image', 'image_url',
                  'additional_images', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """Get full URL for room image"""
        if obj.image:
            return obj.image.url if hasattr(obj.image, 'url') else str(obj.image)
        return None


class GuestSerializer(serializers.ModelSerializer):
    """Serializer for Guest model"""
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Guest
        fields = ['id', 'user', 'first_name', 'last_name', 'full_name', 
                  'email', 'phone_number', 'address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model (online bookings)"""
    guest = GuestSerializer(read_only=True)
    room = RoomListSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=Guest.objects.all(), source='guest', write_only=True
    )
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source='room', write_only=True
    )
    calculated_total = serializers.SerializerMethodField()
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'guest', 'guest_id', 'room', 'room_id', 
                  'check_in_date', 'check_out_date', 'message', 'total_price', 
                  'calculated_total', 'nights', 'paystack_reference', 
                  'paystack_access_code', 'is_paid', 'created_at']
        read_only_fields = ['id', 'total_price', 'paystack_reference', 
                           'paystack_access_code', 'is_paid', 'created_at']
    
    def get_calculated_total(self, obj):
        return float(obj.calculate_total_price())
    
    def get_nights(self, obj):
        if obj.check_in_date and obj.check_out_date:
            return (obj.check_out_date - obj.check_in_date).days
        return 0
    
    def validate(self, data):
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        return data


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservation model"""
    guest = GuestSerializer(read_only=True)
    room = RoomListSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=Guest.objects.all(), source='guest', write_only=True
    )
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source='room', write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = ['id', 'guest', 'guest_id', 'room', 'room_id', 
                  'first_name', 'last_name', 'email', 'phone_number',
                  'check_in_date', 'check_out_date', 'check_in_time', 'check_out_time',
                  'num_adults', 'num_children', 'num_guests', 'status', 'status_display',
                  'price_per_night_at_booking', 'total_price', 'nights',
                  'booking_source', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_nights(self, obj):
        if obj.check_in_date and obj.check_out_date:
            return (obj.check_out_date - obj.check_in_date).days
        return 0


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff model"""
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    
    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'email', 'hotel', 'hotel_name', 
                  'profile_picture', 'position', 'position_display',
                  'department', 'department_display', 'phone_number', 'address',
                  'emergency_contact', 'emergency_phone', 'join_date', 
                  'is_active', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    reservation = ReservationSerializer(read_only=True)
    reservation_id = serializers.PrimaryKeyRelatedField(
        queryset=Reservation.objects.all(), source='reservation', write_only=True
    )
    rating = RatingSerializer(read_only=True)
    rating_id = serializers.PrimaryKeyRelatedField(
        queryset=Rating.objects.all(), source='rating', write_only=True
    )
    guest_name = serializers.CharField(source='reservation.guest.get_full_name', read_only=True)
    hotel_name = serializers.CharField(source='reservation.room.hotel.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'reservation', 'reservation_id', 'rating', 'rating_id', 
                  'comment', 'guest_name', 'hotel_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class ManagerSerializer(serializers.ModelSerializer):
    """Serializer for Manager model"""
    user = UserSerializer(read_only=True)
    hotel_name = serializers.CharField(source='hotel_post.name', read_only=True)
    
    class Meta:
        model = Manager
        fields = ['id', 'user', 'phone', 'hotel_post', 'hotel_name', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for Lead model"""
    class Meta:
        model = Lead
        fields = ['id', 'full_name', 'email', 'phone', 'hotel_name', 
                  'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoomAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking room availability"""
    room_id = serializers.IntegerField()
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    
    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        return data
