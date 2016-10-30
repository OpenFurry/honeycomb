from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from submissions.models import Submission


class Promotion(models.Model):
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
    promoter = models.ForeignKey(User)

    # The date the promotion ends
    promotion_end_date = models.DateTimeField(null=True)


class Ad(models.Model):
    # The ad's owner
    owner = models.ForeignKey(User)

    # The ad's information
    image = models.ImageField()
    adult = models.BooleanField(default=False)
    destination = models.URLField(max_length=4096)


class AdLifecycle(models.Model):
    # The ad to be shown
    ad = models.ForeignKey(Ad)

    # Information about the lifecycle
    cost = models.DecimalField(max_digits=5, decimal_places=2)
    paid = models.BooleanField(default=False)
    live = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Information about the ad's activity
    impressions = models.PositiveIntegerField(default=0)
    interactions = models.PositiveIntegerField(default=0)
