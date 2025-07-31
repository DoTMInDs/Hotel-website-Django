from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, datetime
from decimal import Decimal
import re


class BookingValidator:
    """Validator for booking-related data"""
    
    @staticmethod
    def validate_dates(check_in_date, check_out_date):
        """Validate check-in and check-out dates"""
        if not check_in_date or not check_out_date:
            raise ValidationError(_("Check-in and check-out dates are required."))
        
        if check_in_date >= check_out_date:
            raise ValidationError(_("Check-out date must be after check-in date."))
        
        if check_in_date < date.today():
            raise ValidationError(_("Check-in date cannot be in the past."))
        
        # Check if booking is not too far in the future (e.g., 1 year)
        max_future_date = date.today().replace(year=date.today().year + 1)
        if check_out_date > max_future_date:
            raise ValidationError(_("Bookings cannot be made more than 1 year in advance."))
    
    @staticmethod
    def validate_guest_count(adults, children=0):
        """Validate guest count"""
        if not adults or adults < 1:
            raise ValidationError(_("At least one adult is required."))
        
        if adults > 10:
            raise ValidationError(_("Maximum 10 adults allowed per booking."))
        
        if children > 8:
            raise ValidationError(_("Maximum 8 children allowed per booking."))
        
        total_guests = adults + children
        if total_guests > 10:
            raise ValidationError(_("Maximum 10 guests allowed per booking."))
    
    @staticmethod
    def validate_payment_amount(amount):
        """Validate payment amount"""
        if not amount or amount <= 0:
            raise ValidationError(_("Payment amount must be greater than zero."))
        
        if amount > 1000000:  # 1 million limit
            raise ValidationError(_("Payment amount exceeds maximum limit."))
        
        # Ensure amount is a valid decimal
        try:
            Decimal(str(amount))
        except (ValueError, TypeError):
            raise ValidationError(_("Invalid payment amount."))


class ContactValidator:
    """Validator for contact information"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            raise ValidationError(_("Email is required."))
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(_("Please enter a valid email address."))
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if not phone:
            raise ValidationError(_("Phone number is required."))
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        if len(digits_only) < 10:
            raise ValidationError(_("Phone number must have at least 10 digits."))
        
        if len(digits_only) > 15:
            raise ValidationError(_("Phone number is too long."))
    
    @staticmethod
    def validate_name(name, field_name="Name"):
        """Validate name fields"""
        if not name or not name.strip():
            raise ValidationError(_(f"{field_name} is required."))
        
        if len(name.strip()) < 2:
            raise ValidationError(_(f"{field_name} must be at least 2 characters long."))
        
        if len(name.strip()) > 100:
            raise ValidationError(_(f"{field_name} is too long."))
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        name_pattern = r'^[a-zA-Z\s\'-]+$'
        if not re.match(name_pattern, name.strip()):
            raise ValidationError(_(f"{field_name} contains invalid characters."))


class HotelValidator:
    """Validator for hotel-related data"""
    
    @staticmethod
    def validate_hotel_name(name):
        """Validate hotel name"""
        if not name or not name.strip():
            raise ValidationError(_("Hotel name is required."))
        
        if len(name.strip()) < 3:
            raise ValidationError(_("Hotel name must be at least 3 characters long."))
        
        if len(name.strip()) > 200:
            raise ValidationError(_("Hotel name is too long."))
    
    @staticmethod
    def validate_room_number(room_number):
        """Validate room number"""
        if not room_number or not room_number.strip():
            raise ValidationError(_("Room number is required."))
        
        if len(room_number.strip()) > 10:
            raise ValidationError(_("Room number is too long."))
        
        # Allow alphanumeric room numbers
        room_pattern = r'^[a-zA-Z0-9\-\s]+$'
        if not re.match(room_pattern, room_number.strip()):
            raise ValidationError(_("Room number contains invalid characters."))
    
    @staticmethod
    def validate_price(price):
        """Validate price"""
        if price is None:
            raise ValidationError(_("Price is required."))
        
        try:
            price_decimal = Decimal(str(price))
        except (ValueError, TypeError):
            raise ValidationError(_("Invalid price format."))
        
        if price_decimal < 0:
            raise ValidationError(_("Price cannot be negative."))
        
        if price_decimal > 100000:  # 100k limit
            raise ValidationError(_("Price exceeds maximum limit."))


class FormValidator:
    """General form validation utilities"""
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate that all required fields are present"""
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(_(f"Missing required fields: {', '.join(missing_fields)}"))
    
    @staticmethod
    def validate_file_size(file, max_size_mb=5):
        """Validate file size"""
        if file and file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(_(f"File size must be less than {max_size_mb}MB."))
    
    @staticmethod
    def validate_file_type(file, allowed_types):
        """Validate file type"""
        if file:
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_types:
                raise ValidationError(_(f"File type not allowed. Allowed types: {', '.join(allowed_types)}")) 