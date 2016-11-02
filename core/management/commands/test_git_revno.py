import mock

from django.test import TestCase

from .git_revno import Command


openstr = 'core.management.commands.git_revno.open'


class TestGitRevnoCommand(TestCase):
    @mock.patch('subprocess.check_output')
    def test_set_revno(self, mock_check_output):
        mock_check_output.return_value = 'qwer'
        with mock.patch(openstr, create=True) as mock_open:
            mock_open.return_value = mock.MagicMock()
            cmd = Command()
            cmd.handle(tag='asdf')
        self.assertTrue(mock_open.called)
        f = mock_open.return_value.__enter__.return_value
        f.write.assert_called_with("GIT_REVNO = 'qwer'\nVERSION = 'asdf'\n")
