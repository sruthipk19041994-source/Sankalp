from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile,RoleChoices

class ProfileRegistrationForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ['username', 'email', 'contact', 'address', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove Admin option from role choices
        self.fields['role'].choices = [
            choice for choice in RoleChoices.choices if choice[0] != 'Admin'
        ]

