from subprocess import check_output

from django import template

register = template.Library()


@register.simple_tag
def git_revno():
    return check_output(['git', 'rev-parse', '--verify', 'HEAD']).strip()[-7:]
