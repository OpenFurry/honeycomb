from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from usermgmt import utils

register = template.Library()


@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def render_attributes(value, autoescape=True):
    if value == '':
        return 'No attributes'
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x  # noqa: E731
    to_return = '<dl>'
    for attribute in value.split('\n'):
        k, v = attribute.split('=', 1)
        to_return += '<dt>{}</dt>'.format(utils.ATTRIBUTES[k]['dt'])
        to_return += '<dd>{}</dd>'.format(
            utils.ATTRIBUTES[k]['dd'].format(value=esc(v)))
    to_return += '</dl>'
    return mark_safe(to_return)
