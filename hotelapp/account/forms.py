from django import forms
from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ProfileModel

from core.models import Lead,OurRoom,Booking,Staff

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]
    def __init__(self, *args: Any, **kwargs: Any):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        for fieldname in ["username", "email", "password1", "password2"]:
            self.fields[fieldname].help_text = None 
            
class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'full_name',
            'email',
            'phone',
            'hotel_name',
            'message'
        ]
        exclude = ['hotel']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfileModel
        fields = [
            'full_name',
            'email',
            'phone',
            'profile',
            'gender',
            'nationality',
            'address',
        ]

class OurRoomForm(forms.ModelForm):
    class Meta:
        model = OurRoom
        fields = [
            'room_number',
            'room_type',
            'price',
            'status',
            'max_guests',
            'image',
            'star_rating'
        ]
        exclude = ['hotel']
        widgets = {
            'amenities': forms.Textarea(attrs={'rows': 3}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class BookRoomForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'full_name',
            'email',
            'phone',
            'message',
            'check_in',
            'check_out',
            'check_in_time',
            'check_out_time',
        ]
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }
        def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)  
            super(BookRoomForm, self).__init__(*args, **kwargs)
            
        
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'full_name',
            'email',
            'profile_picture',
            'position',
            'department',
            'phone_number',
            'address',
            'emergency_contact',
            'emergency_phone',
            'notes',
            'is_active'
        ]
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
