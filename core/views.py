from django.core.urlresolvers import reverse
from django.shortcuts import render
from haystack.generic_views import SearchView
from haystack.forms import SearchForm


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
