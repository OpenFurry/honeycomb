from django import forms

from .models import (
    NewsItem,
    PublisherPage,
)


class PublisherForm(forms.ModelForm):
    class Meta:
        model = PublisherPage
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
            'body_raw',
        ]
