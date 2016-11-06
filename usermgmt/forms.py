from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User

from .models import (
    FriendGroup,
    Profile,
)


class RegisterForm(UserCreationForm):
    """A form for registering as a new user"""
    email = forms.EmailField(
        label='Email address',
        required=True,
        help_text="""This email will be used as the primary means of
        contacting you, and will not be shared.""",
        widget=forms.EmailInput(attrs={'placeholder': 'user@example.com'}))

    class Meta:
        model = User
        fields = ('username', 'email')
        field_classes = {
            'username': UsernameField,
            'email': forms.EmailField,
        }


class UpdateProfileForm(forms.ModelForm):
    """A form for updating one's profile."""
    class Meta:
        model = Profile
        fields = (
            'can_see_adult_submissions',
            'display_name',
            'profile_raw',
            'results_per_page',
        )


class GroupForm(forms.ModelForm):
    """A form for creating/updating a user group."""
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label='Group members',
        required=False,
        help_text="Select the members of the group.")

    class Meta:
        model = FriendGroup
        fields = ('name',)
