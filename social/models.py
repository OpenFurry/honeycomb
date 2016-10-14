from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from submissions.models import Submission


class Comment(models.Model):
    # Related users
    owner = models.ForeignKey(User)
    target_object_owner = models.ForeignKey(
        User, related_name='comments_by_others')

    # Related object
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object_model = GenericForeignKey('content_type', 'object_id')

    # Comment body
    ctime = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    deleted = models.BooleanField(default=False)


class Rating(models.Model):
    RATING_CHOICES = (
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
    )

    # The user rating the submission
    owner = models.ForeignKey(User)

    # The submission being rated
    submission = models.ForeignKey(Submission)

    # The rating
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)


class EnjoyItem(models.Model):
    # The user enjoying the submission
    owner = models.ForeignKey(User)

    # The submission being enjoyed
    submission = models.ForeignKey(Submission)

    # The date the submission was enjoyed
    ctime = models.DateTimeField(auto_now_add=True)
