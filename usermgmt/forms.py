from django import forms


class OldRegisterForm(forms.Form):
    username = forms.CharField(
        label='Username',
        required=True,
        help_text="""This will be your username on this system. It can be
        anything you'd like as long as it's not the same as anyone else's.""",
        widget=forms.TextInput(attrs={'placeholder': 'foxyfluff69'}))
    email = forms.EmailField(
        label='Email address',
        required=True,
        help_text="""This email will be used as the primary means of
        contacting you, and will not be shared.""",
        widget=forms.EmailInput(attrs={'placeholder': 'user@example.com'}))
    name = forms.CharField(
        label='Display name',
        required=False,
        help_text="""This is the name that will show up on your profile and
        all of your submissions.  It can be your real name or fan name.""",
        widget=forms.TextInput(attrs={'placeholder': 'V. Vulpes'}))
    password1 = forms.CharField(
        label='Password',
        required=True,
        help_text="""Please enter a strong password; this will be used when
        logging in.""",
        widget=forms.PasswordInput())
    password2 = forms.CharField(
        label='Confirm password',
        required=True,
        help_text="""Please retype your password to confirm.""",
        widget=forms.PasswordInput())

    def clean(self):
        pass

    def save(self):
        pass
