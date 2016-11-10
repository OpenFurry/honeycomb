import hashlib
import re

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.postprocessors import Postprocessor
from markdown.util import etree


TABLEFIX_RE = re.compile(r'<table>')
DLFIX_RE = re.compile(r'<dl>')
ABBRFIX_RE = re.compile(r'<abbr title="([^"]+)">([^</abbr>]+)</abbr>')
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
        return TABLEFIX_RE.sub(
            r'<table class="table table-striped table-hover">', text)


class DLFix(Postprocessor):
    def run(self, text):
        return DLFIX_RE.sub(r'<dl class="dl-indent">', text)


class ABBRFix(Postprocessor):
    def run(self, text):
        return re.sub(
            ABBRFIX_RE,
            r'<abbr data-toggle="tooltip" '
            r'data-placement="bottom" '
            r'title="\1">\2</abbr>', text)


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
        md.postprocessors['dlfix'] = DLFix(md)
        md.postprocessors['abbrfix'] = ABBRFix(md)
