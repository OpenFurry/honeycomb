import re

from django import template
from django.template.defaultfilters import stringfilter

PARAGRAPH_RE = re.compile(r'(</p>)')
register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def get_first_paragraphs(value, num_paragraphs=1):
    paras = PARAGRAPH_RE.split(value)
    if len(paras) < num_paragraphs * 2:
        return value
    return ''.join(paras[:num_paragraphs * 2])
