from subprocess import (
    PIPE,
    Popen,
)

from django import template
from django.conf import settings

register = template.Library()


@register.assignment_tag
def git_revno():
    if settings.DEBUG:
        p = Popen(['git', 'rev-parse', '--verify', 'HEAD'], stdout=PIPE,
                  cwd=settings.BASE_DIR)
        revno, _ = p.communicate()
        return {
            'full': revno.decode('utf-8').strip(),
            'short': revno.decode('utf-8').strip()[:7],
            'version': 'DEBUG',
        }
    else:
        return {
            'full': settings.GIT_REVNO,
            'short': settings.GIT_REVNO[:7],
            'version': settings.VERSION,
        }
