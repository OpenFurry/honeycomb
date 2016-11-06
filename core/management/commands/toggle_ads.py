from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A command for activating/retiring advertisements.

    This should be run on a nightly cron job.
    """
    # Don't forget to add ad:golive/ad:retire activities
    pass
