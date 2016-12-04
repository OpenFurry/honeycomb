from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.models import User
from django.core.paginator import (
    EmptyPage,
    Paginator,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from .forms import (
    NewsItemForm,
    PublisherForm,
)
from .models import (
    NewsItem,
    PublisherPage,
)


def list_publishers(request, page=1):
    if request.user.has_perm('publishers.add_publisherpage'):
        qs = PublisherPage.objects.all()
    else:
        qs = PublisherPage.objects.filter(owner__isnull=False)
    paginator = Paginator(qs, request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        publishers = paginator.page(page)
    except EmptyPage:
        publishers = paginator.page(paginator.num_pages)
    return render(request, 'list_publishers.html', {
        'title': 'Publishers',
        'publishers': publishers,
    })


@login_required
@permission_required('publishers.add_publisherpage')
def create_publisher(request):
    form = PublisherForm()
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            messages.success(request, 'Publisher created')
            return redirect(publisher.get_absolute_url())
    return render(request, 'edit_publisher.html', {
        'title': 'Create publisher',
        'form': form,
    })


def view_publisher(request, publisher_slug=None):
    pass


@login_required
def edit_publisher(request, publisher_slug=None):
    publisher = get_object_or_404(PublisherPage, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', status=403)
    form = PublisherForm(instance=publisher)
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            publisher = form.save()
            messages.success(request, 'Publisher updated')
            return redirect(publisher.get_absolute_url())
    return render(request, 'edit_publisher.html', {
        'title': 'Edit publisher',
        'subtitle': publisher.name,
        'form': form,
    })


@login_required
@permission_required('publishers.delete_publisherpage')
def delete_publisher(request, publisher_slug=None):
    pass


@login_required
@require_POST
def add_member(request, publisher_slug=None):
    user = get_object_or_404(User, username=request.POST.get('username'))
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', status=403)
    if user not in publisher.members.all():
        publisher.members.add(user)
        messages.success(request, 'User added to members')
    else:
        messages.info(request, 'User already in members')
    return redirect(publisher.get_absolute_url())


@login_required
@require_POST
def remove_member(request, publisher_slug=None):
    user = get_object_or_404(User, username=request.POST.get('username'))
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', status=403)
    if user in publisher.members.all():
        publisher.members.remove(user)
        messages.success(request, 'User removed from members')
    else:
        messages.info(request, 'User not in members')
    return redirect(publisher.get_absolute_url())


@login_required
@require_POST
def add_call(request, publisher_slug=None):
    pass


@login_required
@require_POST
def remove_call(request, publisher_slug=None):
    pass


@login_required
@permission_required('publishers.add_publisherpage')
def change_ownership(request, publisher_slug=None):
    pass


def list_news_items(request, publisher_slug=None):
    pass


@login_required
def create_news_item(request, publisher_slug=None):
    pass


def view_news_item(request, publisher_slug=None, item_id=None):
    pass


@login_required
def edit_news_item(request, publisher_slug=None, item_id=None):
    pass


@login_required
def delete_news_item(request, publisher_slug=None, item_id=None):
    pass
