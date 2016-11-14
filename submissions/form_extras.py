from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def append_form_control(value):
    """A filter for adding bootstrap classes to form fields."""
    return value.replace(
            '<input', '<input class="form-control"'
        ).replace(
            '<textarea', '<textarea class="form-control"'
        ).replace(
            '<select', '<select class="form-control"'
        )
