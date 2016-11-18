from __future__ import unicode_literals
import markdown

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.html import strip_tags
from taggit.models import Tag

from .group_models import FriendGroup
from administration.models import Flag
from honeycomb_markdown import HoneycombMarkdown
from submissions.models import Submission


class Profile(models.Model):
    """A user profile."""
    # The user object this profile is tied to
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Some social aspects managed through relations
    blocked_users = models.ManyToManyField(User, related_name='blocked_by')
    watched_users = models.ManyToManyField(User, related_name='watched_by')
    favorited_submissions = models.ManyToManyField(Submission,
                                                   related_name='favorited_by')
    friend_groups = models.ManyToManyField(FriendGroup)

    # Profile information
    display_name = models.CharField(max_length=100, blank=True)
    profile_raw = models.TextField(blank=True, verbose_name='profile text')
    profile_rendered = models.TextField(blank=True)

    # Key/value pairs of simple profile information
    # (favorite genre, editor, etc)
    attributes = models.TextField(blank=True)

    # Content filter settings
    favorite_tags = models.ManyToManyField(Tag, related_name='favorited_by')
    blocked_tags = models.ManyToManyField(Tag, related_name='blocked_by')

    # Additional settings
    banned = models.BooleanField(default=False)
    flags = GenericRelation(Flag)
    can_see_adult_submissions = models.BooleanField(default=True)
    results_per_page = models.PositiveIntegerField(default=25)
    expired_notifications = models.PositiveIntegerField(default=0)

    def get_display_name(self):
        return self.display_name if self.display_name else \
            '~{}'.format(self.user.username)

    def save(self, *args, **kwargs):
        self.profile_rendered = markdown.markdown(
            strip_tags(self.profile_raw),
            extensions=[
                'pymdownx.extra',
                'markdown.extensions.codehilite',
                'pymdownx.headeranchor',
                'pymdownx.magiclink',
                'pymdownx.smartsymbols',
                'pymdownx.tilde',
                'pymdownx.mark',
                HoneycombMarkdown(),
            ])
        super(Profile, self).save(*args, **kwargs)

    def get_notifications_counts(self):
        notifications = self.user.notification_set.all()
        counts = {
            'user_notifications': 0,
            'submission_notifications': 0,
            'messages': 0,
            'admin_notifications': 0,
        }
        for notification in notifications:
            if notification.notification_type == Notification.WATCH:
                counts['user_notifications'] += 1
            elif notification.notification_type == Notification.MESSAGE:
                counts['messages'] += 1
            elif notification.notification_type in \
                    Notification.ADMIN_NOTIFICATIONS:
                counts['admin_notifications'] += 1
            else:
                counts['submission_notifications'] += 1
        return counts

    def get_active_flag(self):
        """Retrieve flag if there is an active flag against this submission"""
        active_flags = self.flags.filter(resolved=None)
        if len(active_flags) > 0:
            return active_flags[0]

    def get_notifications_sorted(self):
        notifications = self.user.notification_set.all()
        sorted_notifications = {
            'Watch': [],
            'Favorite': [],
            'Rating': [],
            'Enjoy': [],
            'Submission_comment': [],
            'Comment_reply': [],
            'Promote': [],
            'Highlight': [],
            'Message': [],
            'Application_claimed': [],
            'Application_resolved': [],
            'admin_notification_count': 0,
            'submission_notification_count': 0,
            'count': 0,
        }

        for notification in notifications:
            sorted_notifications[
                notification.get_notification_type_display().replace(
                    ' ', '_')].append(
                    notification)
            sorted_notifications['count'] += 1
            if notification.notification_type in \
                    Notification.SUBMISSION_NOTIFICATIONS:
                sorted_notifications['submission_notification_count'] += 1
            if notification.notification_type in \
                    Notification.ADMIN_NOTIFICATIONS:
                sorted_notifications['admin_notification_count'] += 1
        return sorted_notifications


class Notification(models.Model):
    """A notification for a user of a pertinent event that has happened."""
    # TODO Move notification to social applcation
    # @makyo 2016-11-05 #58
    WATCH = 'W'
    FAVORITE = 'F'
    MESSAGE = 'M'
    RATING = 'R'
    ENJOY = 'E'
    SUBMISSION_COMMENT = 'S'
    COMMENT_REPLY = 'C'
    PROMOTE = 'P'
    HIGHLIGHT = 'H'
    APPLICATION_CLAIMED = 'c'
    APPLICATION_RESOLVED = 'r'
    FLAG_CREATED_AGAINST = 'f'
    FLAG_PARTICIPANT_JOINED = 'p'
    FLAG_RESOLVED = 's'
    FLAG_COMMENT = 'm'
    NOTIFICATION_TYPE_CHOICES = (
        (WATCH, 'Watch'),
        (MESSAGE, 'Message'),
        (FAVORITE, 'Favorite'),
        (RATING, 'Rating'),
        (ENJOY, 'Enjoy'),
        (SUBMISSION_COMMENT, 'Submission comment'),
        (COMMENT_REPLY, 'Comment reply'),
        (PROMOTE, 'Promote'),
        (HIGHLIGHT, 'Highlight'),
        (APPLICATION_CLAIMED, 'Application claimed'),
        (APPLICATION_RESOLVED, 'Application resolved'),
        (FLAG_CREATED_AGAINST, 'Flag created against'),
        (FLAG_PARTICIPANT_JOINED, 'Flag participant joined'),
        (FLAG_RESOLVED, 'Flag resolved'),
        (FLAG_COMMENT, 'Flag commented on'),
    )
    USER_NOTIFICATIONS = (
        WATCH,
    )
    SUBMISSION_NOTIFICATIONS = (
        FAVORITE,
        RATING,
        ENJOY,
        SUBMISSION_COMMENT,
        COMMENT_REPLY,
        PROMOTE,
        HIGHLIGHT,
    )
    ADMIN_NOTIFICATIONS = (
        APPLICATION_CLAIMED,
        APPLICATION_RESOLVED,
        FLAG_CREATED_AGAINST,
        FLAG_PARTICIPANT_JOINED,
        FLAG_RESOLVED,
        FLAG_COMMENT,
    )

    # The user being notified
    target = models.ForeignKey(User)

    # The user doing the action generating the notification
    source = models.ForeignKey(User, related_name='notification_source',
                               blank=True, null=True)

    # The type of notification
    notification_type = models.CharField(max_length=1,
                                         choices=NOTIFICATION_TYPE_CHOICES)

    # The date of creation
    ctime = models.DateTimeField(auto_now_add=True)

    # The related submission (if applicable)
    subject_content_type = models.ForeignKey(ContentType, blank=True,
                                             null=True)
    subject_id = models.PositiveIntegerField(blank=True, null=True)
    subject = GenericForeignKey('subject_content_type', 'subject_id')

    class Meta:
        ordering = ['-ctime']
