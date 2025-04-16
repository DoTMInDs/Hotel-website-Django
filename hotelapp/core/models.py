from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
    hotel = models.ForeignKey(HotelPost, on_delete=models.CASCADE, related_name='rooms', null=True,blank=True)
    room_type = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0.01)])  # Prevent zero/negative prices
    description = models.TextField(null=True, blank=True)
    available = models.BooleanField(default=True, null=True)
    amenities = models.TextField(blank=True, null=True, help_text="Comma-separated list of amenities")
    check_in_time = models.TimeField(default=timezone.datetime.strptime('15:00', '%H:%M').time())  # 3 PM
    check_out_time = models.TimeField(default=timezone.datetime.strptime('11:00', '%H:%M').time())  # 11 AM
    max_guests = models.PositiveIntegerField(default=2,validators=[MinValueValidator(1), MaxValueValidator(10)])
    bed_type = models.CharField(max_length=100,choices=BED_TYPE_CHOICES,default='double')
    bed_count = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)])
    room_size = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 25 m²")
    room_view = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Ocean View")
    image = models.ImageField(upload_to='rooms/',validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'webp'])])
    star_rating = models.ForeignKey(Rating, on_delete=models.PROTECT)  # Prevent accidental rating deletion
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        indexes = [
            models.Index(fields=['available', 'price']),
            models.Index(fields=['bed_type', 'max_guests']),
        ]

    def __str__(self):
        return f"{self.room_type} - {self.bed_type} Bed"

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
    hotel = models.CharField(max_length=100, null=True)
    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return self.full_name