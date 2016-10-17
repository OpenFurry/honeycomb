from django import forms

from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = (
            'title',
            'description_raw',
            'content_raw',
            'content_file',
            'icon',
            'cover',
            'can_comment',
            'can_enjoy',
            'adult_rating',
            'hidden',
            'restricted_to_groups',
            'allowed_groups',
        )
