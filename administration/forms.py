from django import forms

from .models import (
    Application,
    Ban,
    Flag,
)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('application_type', 'body_raw')
        labels = {
            'application_type': 'I would like to...',
        }
        help_texts = {
            'body_raw': "Tell us about what you'd like to do. Markdown okay!",
        }


class BanForm(forms.ModelForm):
    class Meta:
        model = Ban
        fields = ('end_date', 'reason_raw')


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = ('subject', 'body_raw')
