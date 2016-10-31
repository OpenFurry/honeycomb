from __future__ import unicode_literals

from django.apps import AppConfig


class ActivitystreamConfig(AppConfig):
    name = 'activitystream'

    def ready(self):
        import activitystream.signals  # noqa: F401
