import os
from subprocess import check_output

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        output = check_output(
            ['git', 'rev-parse', '--verify', 'HEAD']).strip()[-7:]
        with open(os.sep.join(['core', 'templates', 'git_revno']), 'w') as f:
            f.write(output)
