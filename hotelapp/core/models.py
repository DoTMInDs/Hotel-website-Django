from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.
class Rating(models.Model):
    star = models.CharField(max_length=10)
    def __str__(self):
        return self.star


class OurRooms(models.Model):
    room_type = models.CharField(max_length=200)
    image = models.ImageField(upload_to='profile', validators=[FileExtensionValidator(['png', 'jpg', 'jfif'])])
    star_rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    
    def __str__(self):
        return self.room_type


class HotelPost(models.Model):
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')
    content = models.TextField(null=True)
    dated_on = models.TimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-dated_on',)
    
    def __str__(self):
        return self.name
    
class Lead(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField(null=True)
    
    def __str__(self):
        return self.full_name