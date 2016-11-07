from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .models import (
    Application,
    # Ban,
    # Flag,
)


@login_required
def dashboard(request):
    """View for displaying a dashboard of administrative objects."""
    query = Q(resolution='')
    if request.user.has_perm('administration.can_list_social_applications'):
        query &= Q(application_type__in=Application.SOCIAL_TYPES)
    if request.user.has_perm('administration.can_list_content_applications'):
        query &= Q(application_type__in=Application.CONTENT_TYPES)
    applications = Application.objects.filter(query)
    return render(request, 'dashboard.html', {
        'tab': 'dashboard',
        'title': 'Administration Dashboard',
        'applications': applications,
        'flags': [],
        'bans': [],
    })
