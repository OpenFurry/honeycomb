from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from submissions.models import Submission


class Promotion(models.Model):
    """A promoted submission.

    A submission may be promoted automatically, a promotion may be purchased
    for a submission, or a content moderator may highlight a submission.
    """
    PROMOTION = 'p'
    PAID_PROMOTION = '$'
    HIGHLIGHT = 'h'
    PROMOTION_TYPE_CHOICES = (
        (PROMOTION, 'Promotion'),
        (PAID_PROMOTION, 'Paid promotion'),
        (HIGHLIGHT, 'Highlight'),
    )

    # The promotion type
    promotion_type = models.CharField(
        max_length=1, choices=PROMOTION_TYPE_CHOICES)

    # The submission being promoted
    submission = models.ForeignKey(Submission)

    # The user promoting the submission
    promoter = models.ForeignKey(User, blank=True, null=True)

    # The date the promotion ends
    promotion_end_date = models.DateField(null=True)

    class Meta:
        permissions = (
            ('can_highlight', 'Can create highlight permissions'),
        )


class Event(models.Model):
    """An event such as NaNoWriMo where tagged submissions are promoted to
    the event's page.
    """
    owner = models.ForeignKey(User)
    announce_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    cover = models.ImageField()
    banner = models.ImageField()
    description_raw = models.TextField()
    description_rendered = models.TextField()
    featured_tag = models.CharField(max_length=100)


class Ad(models.Model):
    """An advertisement submitted to be displayed on the site"""
    # The ad's owner
    owner = models.ForeignKey(User)

    # The ad's information
    image = models.ImageField()
    adult = models.BooleanField(default=False)
    destination = models.URLField(max_length=4096)


class AdLifecycle(models.Model):
    """A lifecycle for a given ad."""
    # The admin scheduling the ad
    admin_contact = models.ForeignKey(User)

    # The ad to be shown
    ad = models.ForeignKey(Ad)

    # Information about the lifecycle
    cost = models.DecimalField(max_digits=5, decimal_places=2)
    paid = models.BooleanField(default=False)
    live = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Information about the ad's activity
    impressions = models.PositiveIntegerField(default=0)
    interactions = models.PositiveIntegerField(default=0)
