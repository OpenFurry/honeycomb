import hashlib
import re

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.postprocessors import Postprocessor
from markdown.util import etree


TABLEFIX_RE = re.compile('<table>')
USERNAME_PATTERN_NAME = r'~([\w-]+)'
USERNAME_PATTERN_ICON = r'@!([\w-]+)'
USERNAME_PATTERN_ICONNAME = r'@([\w-]+)'


class HoneycombUserName(Pattern):
    def handleMatch(self, m):
        el = etree.Element('a')
        el.set('href', reverse('usermgmt:view_profile', args=(m.group(2),)))
        el.set('class', 'name-user-link')
        el.text = '~{}'.format(m.group(2))
        return el


class HoneycombUserIcon(Pattern):
    fetched_users = {}

    def handleMatch(self, m):
        try:
            if m.group(2) in self.fetched_users:
                user = self.fetched_users[m.group(2)]
            else:
                user = User.objects.get(username=m.group(2))
                self.fetched_users[m.group(2)] = user
            el = etree.Element('a')
            el.set('href', reverse('usermgmt:view_profile',
                   args=(m.group(2),)))
            el.set('class', 'icon-user-link')
            el.text = ('![gravatar]'
                       '(https://www.gravatar.com/avatar/{}?s=50)').format(
                           hashlib.md5(
                               user.email.strip().lower().encode('utf-8')
                           ).hexdigest(),
                           m.group(2))
            return el
        except User.DoesNotExist:
            el = etree.Element('a')
            el.set('href', reverse('usermgmt:view_profile',
                   args=(m.group(3),)))
            el.set('class', 'user-link')
            el.text = m.group(2)
            return el


class HoneycombUserIconName(Pattern):
    fetched_users = {}

    def handleMatch(self, m):
        try:
            if m.group(2) in self.fetched_users:
                user = self.fetched_users[m.group(2)]
            else:
                user = User.objects.get(username=m.group(2))
                self.fetched_users[m.group(2)] = user
            el = etree.Element('a')
            el.set('href', reverse('usermgmt:view_profile',
                   args=(m.group(2),)))
            el.set('class', 'icon-name-user-link')
            el.text = ('![gravatar](https://www.gravatar.com/avatar/{}?s=50) '
                       '{}').format(
                           hashlib.md5(
                                   user.email.strip().lower().encode('utf-8')
                           ).hexdigest(),
                           m.group(2))
            return el
        except User.DoesNotExist:
            el = etree.Element('a')
            el.set('href', reverse('usermgmt:view_profile',
                   args=(m.group(3),)))
            el.set('class', 'user-link')
            el.text = m.group(2)
            return el


class TableFix(Postprocessor):
    def run(self, text):
        return TABLEFIX_RE.sub('<table class="table table-hover">', text)


class HoneycombMarkdown(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add(
            'honeycomb_user_icon',
            HoneycombUserIcon(USERNAME_PATTERN_ICON),
            '<image_link')
        md.inlinePatterns.add(
            'honeycomb_user_iconname',
            HoneycombUserIconName(USERNAME_PATTERN_ICONNAME),
            '<image_link')
        md.inlinePatterns['honeycomb_user_name'] = HoneycombUserName(
            USERNAME_PATTERN_NAME)
        md.postprocessors['tablefix'] = TableFix(md)
