import hashlib
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def gravatar_url(email, size=40):
    return 'https://www.gravatar.com/avatar/{}?s={}&d={}'.format(
        hashlib.md5(email.encode('utf-8').lower()).hexdigest(),
        size, 'identicon')


@register.filter
def gravatar(email, size=40):
    url = gravatar_url(email, size)
    return mark_safe(
        '<img alt="gravatar icon" src="{}" height="{}" width="{}" />'.format(
            url, size, size))
