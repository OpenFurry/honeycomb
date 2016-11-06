from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from usermgmt import utils

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def render_attributes(value, autoescape=True):
    """A filter for changing a list of user attributes into a list of links,
    data, etc.
    """
    # TODO
    # @makyo 2016-11-06 #63
    if value == '':
        return 'No attributes'
    to_return = '<dl>'
    for attribute in value.split('\n'):
        k, v = attribute.split('=', 1)
        if k in utils.ATTRIBUTES:
            to_return += '<dt>{}</dt>'.format(utils.ATTRIBUTES[k]['dt'])
            to_return += '<dd>{}</dd>'.format(
                utils.ATTRIBUTES[k]['dd'].format(value=conditional_escape(v)))
    to_return += '</dl>'
    return mark_safe(to_return)
