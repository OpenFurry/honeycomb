from __future__ import print_function
import mock

from django.contrib.flatpages.models import FlatPage
from django.test import TestCase

from .update_flatpages import Command


openstr = 'core.management.commands.update_flatpages.open'
printstr = 'core.management.commands.update_flatpages.mockable_print'


class TestUpdateFlatpages(TestCase):
    @mock.patch(printstr)
    def test_no_create_missing(self, mock_print):
        tos = FlatPage(
            url='/about/terms/',
            title='TOS',
            content='Foo')
        tos.save()
        cmd = Command()
        with mock.patch(openstr, create=True) as mock_open:
            cmd.handle(create_missing=False)
        self.assertTrue(mock_open.called)
        self.assertTrue(
            mock.call('/about/help/api/ does not exist, ignoring.') in
            mock_print.call_args_list)
        self.assertTrue(
            mock.call('/about/terms/ updated.') in mock_print.call_args_list)

    @mock.patch(printstr)
    def test_create_missing(self, mock_print):
        tos = FlatPage(
            url='/about/terms/',
            title='TOS',
            content='Foo')
        tos.save()
        cmd = Command()
        with mock.patch(openstr, create=True) as mock_open:
            cmd.handle(create_missing=True)
        self.assertTrue(mock_open.called)
        self.assertTrue(
            mock.call('/about/help/api/ does not exist, creating.') in
            mock_print.call_args_list)
        self.assertTrue(
            mock.call('/about/terms/ updated.') in mock_print.call_args_list)
