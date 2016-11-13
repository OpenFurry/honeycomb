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

from administration.models import Flag
from honeycomb_markdown import HoneycombMarkdown
from submissions.models import Submission


class Comment(models.Model):
    """A comment posted on a page on the site.

    Comments may be posted on pages for:

    - :model:`submissions.Submission`
    - :model:`promotions.Event`
    - :model:`publishers.Publisher`
    """
    # Related users
    owner = models.ForeignKey(User)
    target_object_owner = models.ForeignKey(
        User, blank=True, null=True, related_name='comments_by_others')

    # Related object (submission, publisher page)
    parent = models.ForeignKey('Comment', blank=True, null=True,
                               related_name='children')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object_model = GenericForeignKey('content_type', 'object_id')

    # Comment body
    ctime = models.DateTimeField(auto_now_add=True)
    body_raw = models.TextField(verbose_name='Comment')
    body_rendered = models.TextField()
    deleted = models.BooleanField(default=False)
    deleted_by_object_owner = models.BooleanField(default=False)

    flags = GenericRelation(Flag)

    def save(self, *args, **kwargs):
        self.body_rendered = markdown.markdown(
            strip_tags(self.body_raw),
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
        super(Comment, self).save(*args, **kwargs)

    def __str__(self):
        return "{}'s comment on {}".format(
            self.owner.profile.get_display_name(),
            str(self.object_model))

    def __unicode__(self):
        return "{}'s comment on {}".format(
            self.owner.profile.get_display_name(),
            str(self.object_model))

    def get_active_flag(self):
        """Retrieve flag if there is an active flag against this submission"""
        active_flags = self.flags.filter(resolved=None)
        if len(active_flags) > 0:
            return active_flags[0]

    def get_absolute_url(self):
        return '{}#comment-{}'.format(
            self.object_model.get_absolute_url(),
            self.id)


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
