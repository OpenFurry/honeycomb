import os
from subprocess import check_output

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('tag', nargs='?', type=str,
                            default='pre-release')

    def handle(self, *args, **kwargs):
        revno = check_output(
            ['git', 'rev-parse', '--verify', 'HEAD']).strip()

        with open(os.sep.join(['honeycomb', 'revno.py']), 'w') as f:
            f.write("GIT_REVNO = '{}'\nVERSION = '{}'\n".format(
                revno, kwargs['tag']))
