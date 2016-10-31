from django.conf import settings
from django.test import (
    TestCase,
    override_settings,
)

from .git_revno import git_revno


class TestGitRevno(TestCase):
    @override_settings(DEBUG=True)
    def test_debug(self):
        revno = git_revno()
        self.assertEqual(len(revno['full']), 40)
        self.assertEqual(len(revno['short']), 7)
        self.assertEqual(revno['version'], 'DEBUG')

    def test_nodebug(self):
        revno = git_revno()
        self.assertEqual(len(revno['full']), 40)
        self.assertEqual(len(revno['short']), 7)
        self.assertEqual(revno['version'], settings.VERSION)
