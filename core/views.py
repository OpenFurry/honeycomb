from django.core.urlresolvers import reverse
from django.shortcuts import render


def front(request):
    return render(request, 'front.html', {})


def flatpage_list(request):
    return render(request, 'flatpages/list.html', {
        'title': 'About',
        'prefix': reverse('core:flatpage_list'),
    })
