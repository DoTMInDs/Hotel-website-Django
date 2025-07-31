from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, time, datetime
from decimal import Decimal
from datetime import timedelta
from cloudinary.models import CloudinaryField # type: ignore

User = get_user_model()
# Create your models here.

class ServiceCategory(models.TextChoices):
    ROOM_SERVICE = 'RS', _('Room Service')
    FOOD_BEVERAGE = "FB", _("Food & Beverage")
    WELLNESS = "WL", _("Wellness")
    TRANSPORTATION = "TR", _("Transportation")
    BUSINESS = "BZ", _("Business")
    LAUNDRY = 'LN', _('Laundry & Dry Cleaning')
    ACTIVITIES = 'AC', _('Activities/Tours')
    CONCIERGE = "CC", _("Concierge")
    FACILITY_RENTAL = 'FR', _('Facility Rental (Meeting Rooms, etc.)')
    OTHER = "OT", _("Other")

class RegionChoices(models.TextChoices):
    GREATER_ACCRA="GA",_("Greater Accra")
    NORTHERN="NR",_("Northern")
    ASHANTI="AS",_("Ashanti")
    CENTRAL="CR",_("Central")
    WESTERN="WR",_("Western")
    VOLTA="VR",_("Volta")
    EASTERN="ER",_("Eastern")
    UPPER_WEST="UW",_("Upper West")
    UPPER_EAST="UE",_("Upper East")
    SAVANNAH="SR",_("Savannah")
    NORTH_EAST="NE",_("North East")
    BONO_EAST="BE",_("Bono East")
    OTI="OR",_("Oti")
    AHAFO="AR",_("Ahafo")
    BONO="BR",_("Bono")
    WESTERN_NORTH="WN",_("Western North")
    
class Rating(models.Model):
    star = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=[(i, f"{i}★") for i in range(1, 6)]
    )
    def __str__(self):
        return f"{self.star}★"

class Amenity(models.Model):
    amenity_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.amenity_name or "Unnamed Amenity"
    
class Hotel(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True, null=True)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    amenities = models.ManyToManyField('Amenity', blank=True, related_name='hotels')
    services = models.ManyToManyField('Service', related_name='hotels_services', blank=True) # New Service ManyToMany
    region=models.CharField(choices=RegionChoices, max_length=2, null=True)
    logo = CloudinaryField(folder='logos/', null=True, blank=True)
    hotel_image = CloudinaryField(folder='hotel_images/', null=True, blank=True,verbose_name=_("Hotel Image"))
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    class Meta:
        verbose_name = _("Hotel")
        verbose_name_plural = _("Hotels")
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['region']),
            models.Index(fields=['-created_at']),
            ]
    
    def __str__(self):
        return self.name
    
class Service(models.Model):
    hotel = models.ManyToManyField('Hotel', related_name='services_hotels', help_text=_("Hotels that offer this service")) # Assuming Hotel model is in 'core' app
    name = models.CharField(max_length=100, help_text=_("Name of the service, e.g., Room Service"),null=True)
    description = models.TextField(blank=True, help_text=_("A brief description of the service"),null=True)
    category = models.CharField(max_length=2,choices=ServiceCategory.choices,default=ServiceCategory.OTHER,help_text=_("Category of the service"))
    is_available = models.BooleanField(default=True, help_text=_("Is this service currently offered?"))
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)],blank=True,null=True,verbose_name=_("Price"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['category', 'name'] # Order services by category and then name

    def __str__(self):
        return self.name

class Room(models.Model):
    BED_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('queen', 'Queen'),
        ('king', 'King'),
    ]
    ROOM_STATUS_CHOICES = ( # Renamed from STATUS_CHOICES to avoid confusion with Reservation status
        ('Available', _('Available')),
        ('Maintenance', _('Maintenance')),
        ('Occupied', _('Occupied')), # Occupied status should ideally be derived from active reservations
        ('Unavailable', _('Temporarily Unavailable')), # For rooms not 'Maintenance' but out of service
    )
    Room_Type = (
        ('standard', 'Standard'),
        ('suite', 'Suite'),
        ('deluxe', 'Deluxe'),
        ('family', 'Family'),
    )
    room_type = models.CharField(max_length=50, choices=Room_Type, default='single')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms', null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0.01)],blank=True, null=True)  # Prevent zero/negative prices
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='rooms', verbose_name=_("Amenities"))
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='Available', verbose_name=_("Physical Status"))
    max_guests = models.PositiveIntegerField(default=2,validators=[MinValueValidator(1), MaxValueValidator(10)])
    bed_type = models.CharField(max_length=100,choices=BED_TYPE_CHOICES,default='double')
    room_number = models.CharField(max_length=10, null=True,verbose_name=_("Room Number"))
    image = CloudinaryField(folder='rooms/')
    star_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL,null=True)  # Prevent accidental rating deletion
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        indexes = [
            models.Index(fields=['status', 'price']),
            models.Index(fields=['room_number', 'max_guests']),
        ]

    def __str__(self):
        return f"{self.room_number} - ({self.get_room_type_display()})"

class Booking(models.Model):
    """
    Booking model for online reservations with payment processing.
    This model handles the initial booking process and payment integration.
    """
    guest = models.ForeignKey('Guest', on_delete=models.CASCADE, related_name='bookings',null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings',null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    message = models.TextField(blank=True, null=True, verbose_name=_("Message"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Payment-related fields
    paystack_reference = models.CharField(max_length=100, blank=True, null=True, unique=True)
    is_paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def calculate_total_price(self):
        if self.room and self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            return Decimal(nights) * (self.room.price or 0)
        return Decimal(0)

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Online Booking'
        verbose_name_plural = 'Online Bookings'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['guest', 'created_at']),
            models.Index(fields=['is_paid', 'created_at']),
            models.Index(fields=['paystack_reference']),
        ]
    
    def __str__(self):
        return f"Online Booking {self.id} by {self.guest.first_name} for {self.room.room_number}"
    
    def clean(self):
        super().clean()
        if self.check_in_date >= self.check_out_date:
            raise ValidationError(_("Check-out date must be after check-in date."))
        
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date
        ).exclude(pk=self.pk)
        if overlapping_bookings.exists():
            raise ValidationError(_("Room is already booked for the selected dates."))
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='guest_profile')
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email Address"))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Phone Number"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Guest")
        verbose_name_plural = _("Guests")
        ordering = ('last_name', 'first_name',)
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        elif self.user:
            return self.user.get_full_name() or self.user.username
        return "Guest"

class OurRoomsImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    image = CloudinaryField(folder='room_images/')
    class Meta:
        verbose_name_plural = 'Our Rooms Images'
        ordering = ('room',)
    
    def __str__(self):
        return self.room.room_type
   
class Manager(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='manager')
    phone = models.CharField(max_length=13, unique=True)
    hotel_post=models.ForeignKey(Hotel,on_delete=models.SET_NULL, null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Lead(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    hotel_name = models.CharField(max_length=100, null=True)
    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return self.full_name
    
class Reservation(models.Model):
    """
    Reservation model for confirmed bookings managed by hotel staff.
    This model handles detailed reservation information including guest details,
    check-in/out times, guest counts, and reservation status tracking.
    Used for both online bookings (after payment confirmation) and manual reservations.
    """
    STATUS_CHOICES = [
        ('Pending', _('Pending Confirmation')), # Booking received, awaiting confirmation
        ('Confirmed', _('Confirmed')), # Booking is confirmed
        ('Checked In', _('Checked In')), # Guest has checked in
        ('Checked Out', _('Checked Out')), # Guest has checked out
        ('Cancelled', _('Cancelled')), # Booking was cancelled
        ('No Show', _('No Show')), # Guest did not arrive and did not cancel
    ]
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name='reservations', verbose_name=_("Guest")) # Use PROTECT - don't delete guest if they have reservations
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='reservations', verbose_name=_("Room")) # Use PROTECT - don't delete room if it has reservations
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"),null=True)
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"),null=True)
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email Address"))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Phone Number"))
    check_in_date = models.DateField(verbose_name=_("Check-in Date"))
    check_out_date = models.DateField(verbose_name=_("Check-out Date"))
    check_in_time = models.TimeField(default=time(15, 0), verbose_name=_("Check-in Time")) # 3 PM
    check_out_time = models.TimeField(default=time(11, 0), verbose_name=_("Check-out Time")) # 11 AM
    num_adults = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_("Number of Adults"))
    num_children = models.PositiveSmallIntegerField(default=0, verbose_name=_("Number of Children"))
    num_guests = models.PositiveSmallIntegerField(default=1,validators=[MinValueValidator(1)],verbose_name=_("Total Number of Guests"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name=_("Status"))
    price_per_night_at_booking = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(0)], verbose_name=_("Price Per Night At Booking"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(0)],verbose_name=_("Total Price"),blank=True, null=True)
    booking_source = models.CharField(max_length=50,blank=True, null=True,verbose_name=_("Booking Source"),help_text=_("e.g., Online, Phone, Walk-in, OTA Name"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes/Requests"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Booked On"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    class Meta:
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")
        ordering = ('check_in_date', 'check_in_time', 'room__room_number',) # Order by check-in time/date
        indexes = [
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['room', 'check_in_date', 'check_out_date']), # Important for availability checks
            models.Index(fields=['guest']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Res #{self.id} for {self.guest} in {self.room} ({self.check_in_date} to {self.check_out_date})"
    
    @classmethod
    def create_from_booking(cls, booking):
        """Create a Reservation from a confirmed Booking"""
        if not booking.is_paid:
            raise ValidationError(_("Cannot create reservation from unpaid booking"))
        
        reservation = cls.objects.create(
            guest=booking.guest,
            room=booking.room,
            first_name=booking.guest.first_name,
            last_name=booking.guest.last_name,
            email=booking.guest.email,
            phone_number=booking.guest.phone_number,
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            price_per_night_at_booking=booking.room.price,
            total_price=booking.total_price,
            status='Confirmed',
            booking_source='Online',
            notes=f"Created from online booking #{booking.id}"
        )
        return reservation
    
    def clean(self):
        super().clean() # Call default clean first
        # --- Date Validation ---
        if self.check_out_date <= self.check_in_date:
            raise ValidationError(_("Check-out date must be strictly after the check-in date."))
        
        # Only check availability if room status is 'Available'
        if self.room.status != 'Available':
            raise ValidationError(_("Room is currently not available for booking."))

        # Check for date conflicts with other reservations
        blocking_statuses = ['Pending', 'Confirmed', 'Checked In']
        overlapping_reservations = Reservation.objects.filter(
            room=self.room,
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date,
            status__in=blocking_statuses
        ).exclude(pk=self.pk)

        if overlapping_reservations.exists():
            overlap = overlapping_reservations.first()
            raise ValidationError(
                _("Room {room_number} is already booked from {overlap_start} to {overlap_end}.").format(
                    room_number=self.room.room_number,
                    overlap_start=overlap.check_in_date,
                    overlap_end=overlap.check_out_date
                )
            )

        # blocking_statuses = ['Pending', 'Confirmed', 'Checked In']

        # if self.room and self.check_in_date and self.check_out_date and self.status in blocking_statuses:
        #     overlapping_reservations = Reservation.objects.filter(
        #         room=self.room,
        #         check_in_date__lt=self.check_out_date,  # Overlap starts before self ends
        #         check_out_date__gt=self.check_in_date,    # Overlap ends after self starts
        #         status__in=blocking_statuses
        #     ).exclude(pk=self.pk) # Exclude self if it's an existing object

        #     if overlapping_reservations.exists():
        #          # Provide details about the first overlapping reservation for context
        #          overlap = overlapping_reservations.first()
        #          raise ValidationError(
        #             _("Room {room_number} is not available "
        #               "from {check_in} to {check_out} "
        #               "due to existing reservation #{res_id} "
        #               "({overlap_start} to {overlap_end}).").format(
        #                 room_number=self.room.room_number,
        #                 check_in=self.check_in_date,
        #                 check_out=self.check_out_date,
        #                 res_id=overlap.id,
        #                 overlap_start=overlap.check_in_date,
        #                 overlap_end=overlap.check_out_date
        #             )
        #          )
        

    

class Staff(models.Model):
    POSITION_CHOICES = [
        ('manager', 'Manager'),
        ('receptionist', 'Receptionist'),
        ('housekeeping', 'Housekeeping'),
        ('maintenance', 'Maintenance'),
        ('chef', 'Chef'),
        ('waiter', 'Waiter'),
        ('security', 'Security'),
        ('other', 'Other'),
    ]

    DEPARTMENT_CHOICES = [
        ('management', 'Management'),
        ('front_desk', 'Front Desk'),
        ('housekeeping', 'Housekeeping'),
        ('food_beverage', 'Food & Beverage'),
        ('maintenance', 'Maintenance'),
        ('security', 'Security'),
        ('other', 'Other'),
    ]
    full_name = models.CharField(max_length=100,null=True)
    email = models.EmailField(null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='staff_members')
    profile_picture = CloudinaryField(folder='staff_profile_pics/', blank=True, null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    join_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Staff"
        ordering = ['-join_date']

    def __str__(self):
        return f"{self.full_name} - {self.get_position_display()}"

class Review(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='review')
    rating = models.ForeignKey(Rating, on_delete=models.PROTECT)  
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.reservation.guest} in {self.reservation.room} ({self.rating})"
    class Meta:
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reservation']),
            models.Index(fields=['rating']),
        ]
    def clean(self):
        super().clean()
        if self.reservation.status != 'Checked Out':
            raise ValidationError(_("Review can only be submitted after check-out."))
        if self.rating.star < 1 or self.rating.star > 5:
            raise ValidationError(_("Rating must be between 1 and 5 stars."))
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    def calculate_average_rating(self):
        """
        Calculate the average rating for a hotel based on all reviews.
        """
        reviews = Review.objects.filter(reservation__room__hotel=self.reservation.room.hotel)
        if reviews.exists():
            total_rating = sum(review.rating.star for review in reviews)
            return total_rating / reviews.count()
        return 0.0
    def get_review_count(self):
        """
        Get the total number of reviews for a hotel.
        """
        return Review.objects.filter(reservation__room__hotel=self.reservation.room.hotel).count()
    def get_average_rating(self):
        """
        Get the average rating for a hotel.
        """
        average_rating = self.calculate_average_rating()
        return f"{average_rating:.1f}★" if average_rating else "No ratings yet"
    def get_review_summary(self):
        """
        Get a summary of reviews for a hotel.
        """
        reviews = Review.objects.filter(reservation__room__hotel=self.reservation.room.hotel)
        summary = {
            'total_reviews': reviews.count(),
            'average_rating': self.calculate_average_rating(),
            'five_star_count': reviews.filter(rating__star=5).count(),
            'four_star_count': reviews.filter(rating__star=4).count(),
            'three_star_count': reviews.filter(rating__star=3).count(),
            'two_star_count': reviews.filter(rating__star=2).count(),
            'one_star_count': reviews.filter(rating__star=1).count(),
        }
        return summary
    def get_review_details(self):
        """
        Get detailed review information for a hotel.
        """
        reviews = Review.objects.filter(reservation__room__hotel=self.reservation.room.hotel)
        details = []
        for review in reviews:
            details.append({
                'guest_name': review.reservation.guest.full_name,
                'rating': review.rating.star,
                'comment': review.comment,
                'created_at': review.created_at,
            })
        return details
   