from __future__ import unicode_literals
import markdown

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.html import strip_tags

from honeycomb_markdown import HoneycombMarkdown
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
    body_raw = models.TextField()
    body_rendered = models.TextField()
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.body_rendered = markdown.markdown(
            strip_tags(self.body_raw),
            extensions=['pymdownx.extra', HoneycombMarkdown()])
        super(Comment, self).save(*args, **kwargs)

    def url(self):
        pass


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

    def get_stars(self):
        return '&#x2605;' * self.rating + '&#x2606;' * (5 - self.rating)


class EnjoyItem(models.Model):
    # The user enjoying the submission
    owner = models.ForeignKey(User)

    # The submission being enjoyed
    submission = models.ForeignKey(Submission)

    # The date the submission was enjoyed
    ctime = models.DateTimeField(auto_now_add=True)
