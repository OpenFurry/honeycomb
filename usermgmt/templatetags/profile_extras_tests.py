from django.test import TestCase

from .profile_extras import render_attributes


class TestRenderAttributes(TestCase):
    def test_no_attributes(self):
        self.assertEqual(render_attributes(''), 'No attributes')

    def test_render_known_attributes(self):
        self.assertEqual(
            render_attributes('twitter=asdf'),
            '<dl><dt>Twitter account</dt><dd><img '
            'src="/static/usermgmt/Twitter_Logo_Blue.png" height="20" />'
            '<a href="https://twitter.com/asdf">asdf</a></dd></dl>')

    def test_skip_unknown_attributes(self):
        self.assertEqual(
            render_attributes('bogus=bad-wolf'),
            '<dl></dl>')
