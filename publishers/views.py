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
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST
from submitify.models import Call

from .forms import (
    NewsItemForm,
    PublisherForm,
)
from .models import (
    NewsItem,
    Publisher,
)


def list_publishers(request, page=1):
    if request.user.has_perm('publishers.add_publisher'):
        qs = Publisher.objects.all()
    else:
        qs = Publisher.objects.filter(owner__isnull=False)
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
@permission_required('publishers.add_publisher')
def create_publisher(request):
    form = PublisherForm()
    if request.method == 'POST':
        form = PublisherForm(request.POST, request.FILES)
        if form.is_valid():
            publisher = form.save()
            messages.success(request, 'Publisher created')
            return redirect(publisher.get_absolute_url())
    return render(request, 'edit_publisher.html', {
        'title': 'Create publisher',
        'form': form,
    })


def view_publisher(request, publisher_slug=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if (publisher.owner is None and not
            request.user.has_perm('publishers.add_publisher')):
        return render(request, 'permission_denied.html', {}, status=403)
    return render(request, 'view_publisher.html', {
        'title': publisher.name,
        'publisher': publisher,
        'tab': 'home',
    })


@login_required
def edit_publisher(request, publisher_slug=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', {}, status=403)
    form = PublisherForm(instance=publisher)
    if request.method == 'POST':
        form = PublisherForm(request.POST, request.FILES, instance=publisher)
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
@permission_required('publishers.delete_publisher')
def delete_publisher(request, publisher_slug=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.method == 'POST':
        publisher.delete()
        messages.error(request, 'Publisher deleted')
        return redirect(reverse('publishers:list_publishers'))
    return render(request, 'confirm_delete_publisher.html', {
        'title': 'Delete publisher',
        'subtitle': publisher.name,
        'publisher': publisher,
    })


@login_required
@require_POST
def add_member(request, publisher_slug=None):
    user = get_object_or_404(User, username=request.POST.get('username'))
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', {}, status=403)
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
        return render(request, 'permission_denied.html', {}, status=403)
    if user in publisher.members.all():
        publisher.members.remove(user)
        messages.success(request, 'User removed from members')
    else:
        messages.info(request, 'User not in members')
    return redirect(publisher.get_absolute_url())


@login_required
@require_POST
def add_editor(request, publisher_slug=None):
    user = get_object_or_404(User, username=request.POST.get('username'))
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', {}, status=403)
    if user not in publisher.editors.all():
        publisher.editors.add(user)
        messages.success(request, 'User added to editors')
    else:
        messages.info(request, 'User already in editors')
    return redirect(publisher.get_absolute_url())


@login_required
@require_POST
def remove_editor(request, publisher_slug=None):
    user = get_object_or_404(User, username=request.POST.get('username'))
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', {}, status=403)
    if user in publisher.editors.all():
        publisher.editors.remove(user)
        messages.success(request, 'User removed from editors')
    else:
        messages.info(request, 'User not in editors')
    return redirect(publisher.get_absolute_url())


def list_calls(request, publisher_slug):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    acceptable_statuses = [Call.OPEN]
    if 'opening-soon' in request.GET:
        acceptable_statuses.append(Call.NOT_OPEN_YET)
    if 'closed-reviewing' in request.GET:
        acceptable_statuses.append(Call.CLOSED_REVIEWING)
    if 'closed-completed' in request.GET:
        acceptable_statuses.append(Call.CLOSED_COMPLETED)
    calls = publisher.calls.filter(status__in=acceptable_statuses)
    available_calls = None
    if request.user == publisher.owner:
        available_calls = Call.objects.filter(
            Q(owner__in=publisher.editors.all()) &
            ~Q(id__in=[call.id for call in calls]))
    return render(request, 'list_publisher_calls.html', {
        'publisher': publisher,
        'calls': calls,
        'available_calls': available_calls,
        'tab': 'calls',
    })


@login_required
@require_POST
def add_call(request, publisher_slug=None):
    call = get_object_or_404(Call, id=request.POST.get('call_id'))
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', {}, status=403)
    if call.owner not in publisher.editors.all():
        return render(request, 'permission_denied.html', {}, status=403)
    if call in publisher.calls.all():
        messages.info(request, '{} already owns this call'.format(
            publisher.name))
    else:
        publisher.calls.add(call)
    return redirect(publisher.get_absolute_url())


@login_required
@require_POST
def remove_call(request, publisher_slug=None):
    call = get_object_or_404(Call, id=request.POST.get('call_id'))
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user != publisher.owner:
        return render(request, 'permission_denied.html', {}, status=403)
    if call.owner not in publisher.editors.all():
        return render(request, 'permission_denied.html', {}, status=403)
    if call not in publisher.calls.all():
        messages.info(request, "{} doesn't own this call".format(
            publisher.name))
    else:
        publisher.calls.remove(call)
    return redirect(publisher.get_absolute_url())


@login_required
@permission_required('publishers.add_publisher')
def change_ownership(request, publisher_slug=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    username = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            publisher.owner = user
            publisher.save()
            publisher.editors.add(user)
            messages.success(request, 'Publisher owner set')
            return redirect(publisher.get_absolute_url())
        except User.DoesNotExist:
            pass
    return render(request, 'change_publisher_ownership.html', {
        'title': 'Change publisher ownership',
        'subtitle': publisher.name,
        'publisher': publisher,
        'username': username,
    })


def list_news_items(request, publisher_slug=None, page=1):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    paginator = Paginator(publisher.newsitem_set.all(),
                          request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        news_items = paginator.page(page)
    except EmptyPage:
        news_items = paginator.page(paginator.num_pages)
    return render(request, 'list_news_items.html', {
        'title': publisher.name,
        'subtitle': 'News',
        'publisher': publisher,
        'news_items': news_items,
    })


@login_required
def create_news_item(request, publisher_slug=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user not in publisher.editors.all():
        return render(request, 'permission_denied.html', {}, status=403)
    form = NewsItemForm()
    if request.method == 'POST':
        form = NewsItemForm(request.POST, request.FILES)
        if form.is_valid():
            news_item = form.save(commit=False)
            news_item.publisher = publisher
            news_item.owner = request.user
            news_item.save()
            form.save_m2m()
            return redirect(news_item.get_absolute_url())
    return render(request, 'edit_news_item.html', {
        'title': 'Create news item',
        'publisher': publisher,
        'form': form,
    })


def view_news_item(request, publisher_slug=None, item_id=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    news_item = get_object_or_404(NewsItem, id=item_id, publisher=publisher)
    return render(request, 'view_news_item.html', {
        'title': news_item.subject,
        'subtitle': publisher.name,
        'publisher': publisher,
        'news_item': news_item,
    })


@login_required
def edit_news_item(request, publisher_slug=None, item_id=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user not in publisher.editors.all():
        return render(request, 'permission_denied.html', {}, status=403)
    item = get_object_or_404(NewsItem, id=item_id, publisher=publisher)
    if request.user not in [item.owner, publisher.owner]:
        return render(request, 'permission_denied.html', {}, status=403)
    form = NewsItemForm(instance=item)
    if request.method == 'POST':
        form = NewsItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            news_item = form.save(commit=False)
            news_item.publisher = publisher
            news_item.owner = request.user
            news_item.save()
            form.save_m2m()
            return redirect(news_item.get_absolute_url())
    return render(request, 'edit_news_item.html', {
        'title': 'Edit news item',
        'subtitle': item.subject,
        'publisher': publisher,
        'form': form,
    })


@login_required
def delete_news_item(request, publisher_slug=None, item_id=None):
    publisher = get_object_or_404(Publisher, slug=publisher_slug)
    if request.user not in publisher.editors.all():
        return render(request, 'permission_denied.html', {}, status=403)
    item = get_object_or_404(NewsItem, id=item_id, publisher=publisher)
    if request.user not in [item.owner, publisher.owner]:
        return render(request, 'permission_denied.html', {}, status=403)
    if request.method == 'POST':
        item.delete()
        return redirect(publisher.get_absolute_url())
    return render(request, 'confirm_delete_newsitem.html', {
        'title': 'Delete news item',
        'subtitle': item.subject,
        'publisher': publisher,
        'news_item': item,
    })
