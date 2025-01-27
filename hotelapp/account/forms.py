from django import forms
from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ProfileModel

from core.models import Lead

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
            'message'
        ]


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