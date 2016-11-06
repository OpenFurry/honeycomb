from django import forms

from .models import (
    Folder,
    Submission,
)


class SubmissionForm(forms.ModelForm):
    """Form for submitting/editing a submission."""
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
            'folders',
            'tags',
        )


class FolderForm(forms.ModelForm):
    """Form for creating/editing a folder."""
    class Meta:
        model = Folder
        fields = (
            'name',
            'parent',
        )
