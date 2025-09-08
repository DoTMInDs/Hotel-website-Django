from django import forms
from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateInput, TimeInput
from .models import ProfileModel
from core.models import Lead,Room,Reservation,Staff,Booking,Hotel,Amenity,Service,CustomUser

class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
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
            'first_name',
            'last_name',
            'email',
            'phone',
            'profile',
            'gender',
            'nationality',
            'address',
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = ProfileModel
        fields = ['first_name', 'last_name', 'phone', 'nationality', 'gender', 'address', 'profile']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter your last name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter your phone number'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter your nationality'
            }),
            'gender': forms.Select(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
            'address': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter your address'
            }),
            'profile': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
        }

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
            # 'star_rating',
            'amenities',
        ]
        exclude = ['hotel']
        widgets = {
            'room_number': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter room number'
            }),
            'room_type': forms.Select(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter price per night',
                'step': '0.01',
                'min': '0'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
            'max_guests': forms.NumberInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Maximum number of guests',
                'min': '1',
                'max': '10'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
            'amenities': forms.SelectMultiple(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'size': '5'
            }),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'check_in_date',
            'check_out_date',
            'message',
        ]
        exclude = ['guest', 'room']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                raise forms.ValidationError("Check-out date must be after check-in date.")
        
        return cleaned_data

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
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter phone number'
            }),
            'room': forms.Select(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
            'check_in_date': forms.DateInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'type': 'date'
            }),
            'check_out_date': forms.DateInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'type': 'date'
            }),
            'check_in_time': forms.TimeInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'type': 'time'
            }),
            'check_out_time': forms.TimeInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'type': 'time'
            }),
            'num_adults': forms.NumberInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Number of adults',
                'min': '1',
                'max': '10'
            }),
            'num_children': forms.NumberInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Number of children',
                'min': '0',
                'max': '10'
            }),
            'num_guests': forms.NumberInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Total number of guests',
                'min': '1',
                'max': '10'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'rows': 3,
                'placeholder': 'Additional notes or special requests'
            }),
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
            'join_date',
            'is_active',
            'notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter phone number'
            }),
            'position': forms.Select(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
            'department': forms.Select(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
            'address': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-3 shadow rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'rows': 2,
                'placeholder': 'Enter address'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Emergency contact phone'
            }),
            'join_date': forms.DateInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-3 shadow  rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
        }

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'location', 'region', 'phone_number', 'email', 'description', 'hotel_image', 'logo', 'amenities']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter hotel name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter hotel location'
            }),
            'region': forms.Select(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Enter email address'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'rows': 4,
                'placeholder': 'Enter hotel description'
            }),
            'hotel_image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
            'amenities': forms.SelectMultiple(attrs={
                'class': 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'
            }),
        }

class AddAmenitiesForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['amenity_name']

    def clean_amenity_name(self):
        name = self.cleaned_data.get('amenity_name')
        if not name:
            raise forms.ValidationError("Amenity name is required.")
        return name

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'category', 'is_available']    
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }   