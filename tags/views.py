from django.contrib.auth.decorators import login_required
from django.core.paginator import (
    EmptyPage,
    Paginator,
)
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    render,
)
from taggit.models import Tag

from submissions.models import Submission
from submissions.utils import (
    filters_for_anonymous_user,
    filters_for_authenticated_user,
)


def list_tags(request):
    return render(request, 'list_tags.html', {
        'title': 'Submission tags',
        'tags': Tag.objects.all(),
    })


def view_tag(request, tag_slug=None, page=1):
    tag = get_object_or_404(Tag, slug=tag_slug)
    filters = filters_for_authenticated_user(request.user) if \
        request.user.is_authenticated else filters_for_anonymous_user()
    results = Submission.objects.filter(
        Q(tags__in=[tag]) & filters)
    paginator = Paginator(results, request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    return render(request, 'view_tag.html', {
        'title': 'Submissions tagged "{}"'.format(tag.name),
        'tag': tag,
        'submissions': submissions,
    })


@login_required
def favorite_tag(request, tag_slug=None):
    pass


@login_required
def unfavorite_tag(request, tag_slug=None):
    pass


@login_required
def list_submissions_with_favorite_tags(request):
    pass


@login_required
def block_tag(request, tag_slug=None):
    pass


@login_required
def unblock_tag(request, tag_slug=None):
    pass
