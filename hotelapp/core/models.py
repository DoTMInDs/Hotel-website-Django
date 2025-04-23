from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
User = get_user_model()
# Create your models here.

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
    amenity_name = models.CharField(max_length=50, null=True)
    
    def __str__(self):
        return self.amenity_name
    
class HotelPost(models.Model):
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=13, unique=True, null=True)
    location = models.CharField(max_length=50)
    region=models.CharField(choices=RegionChoices, max_length=2, null=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, validators=[FileExtensionValidator(['png', 'jpg','jpeg', 'jfif'])])
    dated_on = models.DateTimeField(auto_now_add=True,null=True)
    
    class Meta:
        ordering = ('-dated_on',)
        indexes = [models.Index(fields=['-dated_on'])]
    
    def __str__(self):
        return self.name

class OurRoom(models.Model):
    BED_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('queen', 'Queen'),
        ('king', 'King'),
    ]
    STATUS_CHOICES = (
        ('A', 'Available'),
        ('M', 'Maintenance'),
        ('O', 'Occupied'),
    )
    hotel = models.ForeignKey(HotelPost, on_delete=models.CASCADE, related_name='rooms', null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0.01)])  # Prevent zero/negative prices
    amenities = models.ManyToManyField(Amenity, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A',null=True)
    check_in_date = models.DateField(auto_now_add=True,null=True)
    check_out_date = models.DateField(auto_now_add=True,null=True)
    check_in_time = models.TimeField(default=timezone.datetime.strptime('15:00', '%H:%M').time())  # 3 PM
    check_out_time = models.TimeField(default=timezone.datetime.strptime('11:00', '%H:%M').time())  # 11 AM
    max_guests = models.PositiveIntegerField(default=2,validators=[MinValueValidator(1), MaxValueValidator(10)])
    room_type = models.CharField(max_length=100,choices=BED_TYPE_CHOICES,default='double')
    room_number = models.CharField(max_length=10, null=True)
    image = models.ImageField(upload_to='rooms/',validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'webp'])])
    star_rating = models.ForeignKey(Rating, on_delete=models.PROTECT)  # Prevent accidental rating deletion
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


    
# class Reservation(models.Model):
#     STATUS_CHOICES = (
#         ('C', 'Confirmed'),
#         ('I', 'Checked-in'),
#         ('O', 'Checked-out'),
#         ('X', 'Cancelled'),
#     )
#     guest = models.ForeignKey('Guest', on_delete=models.CASCADE)
#     room = models.ForeignKey(OurRoom, on_delete=models.CASCADE)
#     check_in = models.DateField()
#     check_out = models.DateField()
#     status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='C')
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def clean(self):
#         # Validate that check_out is after check_in
#         if self.check_out <= self.check_in:
#             raise ValidationError("Check-out date must be after check-in date")
        
#         # Check room availability if this is a new reservation
#         if not self.pk and not is_room_available(self.room.id, self.check_in, self.check_out):
#             raise ValidationError("Room is not available for the selected dates")
    
#     def __str__(self):
#         return f"Reservation {self.id} for {self.guest}"


class OurRoomsImage(models.Model):
    room = models.ForeignKey(OurRoom, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='room_images', validators=[FileExtensionValidator(['png', 'jpg','jpeg', 'jfif'])])
    class Meta:
        verbose_name_plural = 'Our Rooms Images'
        ordering = ('room',)
    
    def __str__(self):
        return self.room.room_type
   
class Manager(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='manager')
    phone = models.CharField(max_length=13, unique=True)
    hotel_post=models.ForeignKey(HotelPost,on_delete=models.SET_NULL, null=True,blank=True)
    
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
    
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    hotel = models.ForeignKey(HotelPost, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    room = models.ForeignKey(OurRoom, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, unique=True)
    check_in_time = models.TimeField(default=timezone.datetime.strptime('15:00', '%H:%M').time())  # 3 PM
    check_out_time = models.TimeField(default=timezone.datetime.strptime('11:00', '%H:%M').time())  # 11 AM
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        if self.room and self.hotel:
            return f"Booking #{self.id} - {self.room.room_number} at {self.hotel.name}"
        return f"Booking #{self.id}"


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
    hotel = models.ForeignKey(HotelPost, on_delete=models.CASCADE, related_name='staff_members')
    profile_picture = models.ImageField(upload_to='staff_profile_pics/', blank=True, null=True)
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

 

