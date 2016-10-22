from subprocess import (
    PIPE,
    Popen,
)

from django import template
from django.conf import settings

register = template.Library()


@register.assignment_tag
def git_revno():
    p = Popen(['git', 'rev-parse', '--verify', 'HEAD'], stdout=PIPE,
              cwd=settings.BASE_DIR)
    out, _ = p.communicate()
    return {
        'full': out,
        'short': out.strip()[:7],
    }
