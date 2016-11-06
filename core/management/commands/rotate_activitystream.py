from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A command for rotating the activity stream like a log.

    This should be run from a cron job on a regular basis as specified in
    settings.py
    """
    pass
