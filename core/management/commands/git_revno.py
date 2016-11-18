import os
import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A command for storing the git revno and release in a settings addition.
    """

    def add_arguments(self, parser):
        """Adds arguments via argparse"""
        parser.add_argument('tag', nargs='?', type=str,
                            default='pre-release')

    def handle(self, *args, **kwargs):
        """Generates the addition git settings.

        This generates two settings: `GIT_REVNO` for the current commit hash,
        and `VERSION` for the specified tag.
        """
        revno = subprocess.check_output(
            ['git', 'rev-parse', '--verify', 'HEAD']).strip()
        try:
            revno = revno.decode()
        except:
            pass

        with open(os.sep.join(['honeycomb', 'revno.py']), 'w') as f:
            f.write("GIT_REVNO = '{}'\nVERSION = '{}'\n".format(
                str(revno), kwargs['tag']))
