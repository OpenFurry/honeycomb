from __future__ import unicode_literals
import markdown

from django.contrib.auth.models import (
    Group,
    User,
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.html import strip_tags

from submissions.models import Submission


class Profile(models.Model):
    # The user object this profile is tied to
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Some social aspects managed through relations
    blocked_users = models.ManyToManyField(User, related_name='blocked_by')
    watched_users = models.ManyToManyField(User, related_name='watched_by')
    favorited_submissions = models.ManyToManyField(Submission,
                                                   related_name='favorited_by')
    user_groups = models.ManyToManyField(Group)

    # Profile information
    display_name = models.CharField(max_length=100)
    profile_raw = models.TextField(blank=True, verbose_name='profile text')
    profile_rendered = models.TextField(blank=True)

    # Key/value pairs of simple profile information
    # (favorite genre, editor, etc)
    attributes = models.TextField(blank=True)

    # Additional settings
    can_see_adult_submissions = models.BooleanField(default=True)
    results_per_page = models.PositiveIntegerField(default=25)

    def get_display_name(self):
        return self.display_name if self.display_name else self.user.username

    def save(self, *args, **kwargs):
        self.profile_rendered = markdown.markdown(
            strip_tags(self.profile_raw),
            extension=['markdown.extensions.extra'])
        super(Profile, self).save(*args, **kwargs)


class Notification(models.Model):
    FAVORITE = 'F'
    RATING = 'R'
    ENJOY = 'E'
    WATCH = 'W'
    MESSAGE = 'M'
    SUBMISSION_COMMENT = 'S'
    COMMENT_REPLY = 'C'
    PROMOTE = 'P'
    HIGHLIGHT = 'H'
    NOTIFICATION_TYPE_CHOICES = (
        (FAVORITE, 'Favorite'),
        (RATING, 'Rating'),
        (ENJOY, 'Enjoy'),
        (WATCH, 'Watch'),
        (MESSAGE, 'Message'),
        (SUBMISSION_COMMENT, 'Submission omment'),
        (COMMENT_REPLY, 'Comment reply'),
        (PROMOTE, 'Promote'),
        (HIGHLIGHT, 'Highlight'),
    )

    # The user being notified
    target = models.ForeignKey(User)

    # The user doing the action generating the notification
    source = models.ForeignKey(User, related_name='notification_source')

    # The type of notification
    notification_type = models.CharField(max_length=1)

    # The related submission (if applicable)
    subject_content_type = models.ForeignKey(ContentType)
    subject_id = models.PositiveIntegerField()
    subject = GenericForeignKey('subject_content_type', 'subject_id')
