from django import forms
from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ProfileModel

from core.models import Lead,OurRoom

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
            'hotel',
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
            'room_type',
            'price',
            'available',
            'amenities',
            'check_in_time',
            'check_out_time',
            'max_guests',
            'bed_type',
            'bed_count',
            'image',
            'star_rating'
        ]
        exclude = ['hotel']
        widgets = {
            'amenities': forms.Textarea(attrs={'rows': 3}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
        }