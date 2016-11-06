from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Flag(models.Model):
    """Represents an item flagged for administrative attention."""
    # The object being flagged
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object_model = GenericForeignKey('content_type', 'object_id')

    # The user who flagged the object
    flagged_by = models.ForeignKey(User)

    # Flag information
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.DateTimeField(null=True)
    subject = models.CharField(max_length=100)
    body = models.TextField()
