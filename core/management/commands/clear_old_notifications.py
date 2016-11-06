from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A management command for clearing outdated notifications.

    This should be run from a cron job on a regular basis as specified in
    settings.py
    """
    pass
