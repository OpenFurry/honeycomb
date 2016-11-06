from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A command for creating/retiring promotions.

    This should be run on a nightly cron job.
    """
    # Don't forget to add a promotion:retire activity
    pass
