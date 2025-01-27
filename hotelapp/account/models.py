from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User 
from django.core.validators import EmailValidator
from django.core.validators import FileExtensionValidator

# Create your models here.
class Gender(models.TextChoices):
    MALE="M",_("Male")
    FEMALE="F",_("Female")


class ProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200, null=True)
    profile = models.ImageField(default='default.png', upload_to='profile', validators=[FileExtensionValidator(['png', 'jpg', 'jfif'])])
    phone = models.CharField(max_length=20,null=True)
    email=models.EmailField(validators=[EmailValidator],null=True)
    gender=models.CharField(max_length=1,choices=Gender,null=True)
    nationality = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=200,null=True)    
    
    def __str__(self):
        return f'Profile of {self.user}'
