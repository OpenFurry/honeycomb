from datetimewidget.widgets import DateWidget
from django import forms

from .models import (
    Application,
    Ban,
    Flag,
)


dateTimeOptions = {
    'format': 'yyyy-mm-dd',
}


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
        fields = ('user', 'end_date', 'reason_raw', 'flag')
        widgets = {
            'end_date': DateWidget(options=dateTimeOptions,
                                   attrs={
                                       'id': 'id_dateTimeField',
                                   },
                                   bootstrap_version=3),
            'user': forms.HiddenInput(),
            'flag': forms.HiddenInput(),
        }


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = (
            'subject',
            'flag_type',
            'body_raw',
            'content_type',
            'object_id')
        widgets = {
            'content_type': forms.HiddenInput(),
            'object_id': forms.HiddenInput(),
        }
