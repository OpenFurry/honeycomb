from django.core.urlresolvers import reverse
from django.shortcuts import render
from haystack.generic_views import SearchView
from haystack.forms import SearchForm

from activitystream.models import Activity


def front(request):
    return render(request, 'front.html', {})


def flatpage_list(request):
    return render(request, 'flatpages/list.html', {
        'title': 'About',
        'prefix': reverse('core:flatpage_list'),
    })


class BasicSearchView(SearchView):
    template_name = 'search/search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        if request.GET.get('page') is None:
            Activity.create(
                'search',
                'search',
                request.user if request.user.is_authenticated else None)
        return super(BasicSearchView, self).get(request, *args, **kwargs)
