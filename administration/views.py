from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .models import (
    Application,
    Ban,
    Flag,
)


@login_required
def dashboard(request):
    """View for displaying a dashboard of administrative objects."""
    perms = {
        'administration.can_list_social_applications':
            Application.SOCIAL_TYPES,
        'administration.can_list_content_applications':
            Application.CONTENT_TYPES,
    }

    # Only select unresolve applications
    query = Q(resolution='')

    # Superusers get all applications
    if not request.user.is_superuser:
        # Staff only get applications according to their permissions as well as
        # their own applications
        for perm, allowed_types in perms.items():
            if request.user.has_perm(perm):
                query &= (Q(application_type__in=allowed_types) |
                          Q(applicant=request.user))

        # Non-staff only get their own applications
        if not request.user.is_staff:
            query &= Q(applicant=request.user)
    applications = Application.objects.filter(query)

    # List flags
    perms = {
        'administration.can_list_social_flags':
            Flag.SOCIAL,
        'administration.can_list_content_flags':
            Flag.CONTENT,
    }

    # Only select unresolve flags
    query = Q(resolved=None)

    # Superusers get all flags
    if not request.user.is_superuser:
        # Staff only get flags according to their permissions as well as
        # their own flags
        for perm, allowed_type in perms.items():
            if request.user.has_perm(perm):
                query &= (Q(flag_type=allowed_type) |
                          Q(participants__in=[request.user]))

        # Non-staff only get their own flags
        if not request.user.is_staff:
            query &= Q(participants__in=[request.user])
    flags = Flag.objects.filter(query)

    if request.user.has_perm('administration.can_list_bans'):
        bans = Ban.objects.filter(active=True, end_date__isnull=False)
    else:
        bans = []
    return render(request, 'dashboard.html', {
        'tab': 'dashboard',
        'title': 'Administration Dashboard',
        'applications': applications,
        'flags': flags,
        'bans': bans,
    })
