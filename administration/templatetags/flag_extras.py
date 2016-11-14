from django import template

from administration.models import Flag

register = template.Library()


@register.filter
def can_view_flagged_item(user, flag):
    """A filter for deciding if a user can view a flagged item."""
    if user in flag.participants.all():
        return True
    if user.has_perm('administration.can_view_social_flags') and \
            flag.flag_type == Flag.SOCIAL:
        return True
    if user.has_perm('administration.can_view_content_flags') and \
            flag.flag_type == Flag.CONTENT:
        return True
    return False
