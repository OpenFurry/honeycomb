from django import forms

from .models import (
    NewsItem,
    Publisher,
)


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = [
            'name',
            'url',
            'logo',
            'banner',
            'body_raw',
        ]


class NewsItemForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = [
            'image',
            'subject',
            'body_raw',
        ]
