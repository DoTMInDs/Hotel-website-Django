from django import forms
from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import DateInput, TimeInput
from .models import ProfileModel
from core.models import Lead,Room,Reservation,Staff,Booking,Hotel,Amenity,Service

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

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_number',
            'room_type',
            'price',
            'status',
            'max_guests',
            'image',
            'star_rating',
            'amenities',
        ]
        exclude = ['hotel']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'check_in_date',
            'check_out_date',
            'message',
            'room',
        ]
        exclude = ['guest']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'room', 'check_in_date', 'check_out_date', 
            'check_in_time', 'check_out_time', 'num_adults',
            'num_children', 'num_guests', 'notes'
        ]
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        hotel = kwargs.pop('hotel', None)
        super().__init__(*args, **kwargs)
        if hotel:
            self.fields['room'].queryset = Room.objects.filter(hotel=hotel, status='Available')
    
    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                raise forms.ValidationError("Check-out date must be strictly after the check-in date.")
        
        return cleaned_data
            
        
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

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = [
            'name',
            'email',
            'phone_number',
            'location',
            'region',
            'description',
            'amenities',
            'logo'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AddAmenitiesForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = [
            'amenity_name'
        ]
        widgets = {
            'amenity_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'category', 'is_available']    
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }   