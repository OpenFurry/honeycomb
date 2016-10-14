from django import template
from django.template.defaultfilters import stringfilter

from usermgmt import utils

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def render_attributes(value):
    to_return = '<dl>'
    for attribute in value.split('\n'):
        k, v = attribute.split('=', 1)
        to_return += '<dt>{}</dt>'.format(utils.ATTRIBUTES[k]['dt'])
        to_return += '<dd>{}</dd>'.format(utils.ATTRIBUTES[k]['dd'].format(v))
    to_return = '</dl>'
