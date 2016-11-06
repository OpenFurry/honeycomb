from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from haystack.generic_views import SearchView
from haystack.forms import SearchForm

from activitystream.models import Activity
from activitystream.views import _get_sitewide_data
from submissions.models import Submission
from submissions.utils import (
    filters_for_anonymous_user,
    filters_for_authenticated_user,
)


@cache_page(60 * 5)
def front(request):
    """View for the front page of the site."""
    # Provide logged-in users with a greeting as the subtitle
    greetings = settings.GREETINGS if hasattr(settings, 'GREETINGS') else [
        'Good to see you out and about',
        'You look spectacular today',
        'Read anything good lately?',
        "What's your favorite genre?",
        "Who's your favorite author?",
        'Hope your writing is going well',
        "Keep on keepin' on"
    ]

    # Get a list of activities on the site for a static activity stream
    # TODO replace this with a dynamic fetch for better caching
    # @makyo 2016-11-06 #52
    static_stream = Activity.objects.filter(
        activity_type__in=[
            'comment:create',
            'social:favorite',
            'social:rate',
            'social:enjoy',
            'submission:create',
            'tag:create',
            'publisher:create',
        ])[:10]

    # Get a list of recent submissions on the site
    recent_submissions = Submission.objects.filter(
        filters_for_authenticated_user(request.user) if
        request.user.is_authenticated() else filters_for_anonymous_user()
    ).order_by('-ctime')[:10]

    # Get sitewide data for a static overview of the site
    # TODO replace this with a dynamic fetch for better caching
    # @makyo 2016-11-06 #52
    static_sitewide_data = _get_sitewide_data()
    return render(request, 'front.html', {
        'greetings': greetings,
        'static_sitewide_data': static_sitewide_data,
        'static_stream': static_stream,
        'recent_submissions': recent_submissions,
    })


@cache_page(60 * 60 * 24)
def flatpage_list(request):
    """View for listing all flatpages in the site."""
    return render(request, 'flatpages/list.html', {
        'title': 'About',
        'prefix': reverse('core:flatpage_list'),
    })


@cache_page(60 * 60 * 24)
def helppage_list(request):
    """View for listing only the help flatpages in the site."""
    return render(request, 'flatpages/list.html', {
        'title': 'Help',
        'prefix': reverse('core:helppage_list'),
    })


class BasicSearchView(SearchView):
    """View for searching submissions on the site."""
    # TODO implement in a more understandable way
    # @makyo 2016-11-06 #37
    template_name = 'search/search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        """Gets the search results and creates an activity if needed."""
        if (request.GET.get('page') is None
                and request.GET.get('q') is not None):
            Activity.create(
                'search',
                'basic_search',
                request.user if request.user.is_authenticated else None)
        return super(BasicSearchView, self).get(request, *args, **kwargs)
