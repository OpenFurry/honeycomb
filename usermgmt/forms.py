from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User

from .models import (
    FriendGroup,
    Profile,
)


class RegisterForm(UserCreationForm):
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
    class Meta:
        model = Profile
        fields = ('display_name', 'profile_raw')


class GroupForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label='Group members',
        required=False,
        help_text="Select the members of the group.")

    class Meta:
        model = FriendGroup
        fields = ('name',)
