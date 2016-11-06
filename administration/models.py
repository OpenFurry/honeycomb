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
    flagged_object_owner = models.ForeignKey(User, blank=True, null=True,
                                             related_name="flagged_objects")

    # The user who flagged the object
    flagged_by = models.ForeignKey(User)

    # Flag information
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.DateTimeField(null=True)
    resolved_by = models.ForeignKey(User, related_name='resolved_flags')
    subject = models.CharField(max_length=100)
    body = models.TextField()


class Ban(models.Model):
    """Represents a temporary or permanent ban on a user."""
    # The user being banned
    user = models.ForeignKey(User)

    # The admin who banned the user
    admin_contact = models.ForeignKey(User, related_name='banned_users')

    # The time period of the ban
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True)

    # The reason for the ban
    reason_raw = models.TextField()
    reason_rendered = models.TextField()

    # Any administrative flags if applicable
    flag = models.ManyToManyField(Flag, blank=True)
