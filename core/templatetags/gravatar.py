import hashlib
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def gravatar_url(email, size=40):
    """Generate a gravatar url from an email address.

    Args:
        email: the email address to generate
        size: the size of one side of the icon to generate

    Returns:
        The gravatar URL for the icon.
    """
    return 'https://www.gravatar.com/avatar/{}?s={}&d={}'.format(
        hashlib.md5(email.encode('utf-8').lower()).hexdigest(),
        size, 'identicon')


@register.filter
def gravatar(email, size=40):
    """Generate a gravatar image tag.

    Args:
        email: the email address to generate
        size: the size of one side of the icon to generate

    Returns:
        The image tag for the icon.
    """
    url = gravatar_url(email, size)
    return mark_safe(
        '<img alt="gravatar icon" src="{}" height="{}" width="{}" />'.format(
            url, size, size))
