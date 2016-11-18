from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
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
from taggit.models import Tag

from administration.models import Flag
from submissions.models import Submission
from submissions.utils import (
    filters_for_anonymous_user,
    filters_for_authenticated_user,
)


def list_tags(request):
    """View for listing all tags as a tag cloud."""
    return render(request, 'list_tags.html', {
        'title': 'Submission tags',
        'tags': Tag.objects.all(),
    })


def view_tag(request, tag_slug=None, page=1):
    """View for listing all submissions tagged with a tag.

    Args:
        tag_slug: the slug of the tag to list
        page: the current page for pagination
    """
    tag = get_object_or_404(Tag, slug=tag_slug)

    # Check for admin flags, only show the tag if there are none or the user
    # has permissions to the flag
    ctype = ContentType.objects.get(app_label='taggit', model='tag')
    flags = Flag.objects.filter(content_type=ctype, object_id=tag.id,
                                resolved=None)
    if len(flags) > 0:
        active_flag = flags[0]
    else:
        active_flag = None
    if active_flag is not None and not (
            request.user in active_flag.participants.all() or
            request.user.has_perm('administration.can_view_social_flags') or
            request.user.has_perm('administration.can_view_content_flags')):
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
            'additional_error': 'This tag has been flagged for '
                                'administrative review',
        }, status=403)

    # Filter submissions visible to the reader
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
        'active_flag': active_flag,
        'submissions': submissions,
    })


@login_required
@require_POST
def favorite_tag(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    if tag in request.user.profile.favorite_tags.all():
        messages.warning(request, "You have already favorited that tag")
    else:
        request.user.profile.favorite_tags.add(tag)
        messages.success(request, "Tag favorited; submissions tagged with {} "
                         "will show up in the list of submissions with your "
                         "favorited tags".format(tag.name))
    return redirect(reverse('tags:view_tag', kwargs={'tag_slug': tag.slug}))


@login_required
@require_POST
def unfavorite_tag(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    if tag not in request.user.profile.favorite_tags.all():
        messages.warning(request, "You haven't favorited that tag")
    else:
        request.user.profile.favorite_tags.remove(tag)
        messages.success(request, "Tag unfavorited; submissions tagged with "
                         "{} will no longershow up in the list of "
                         "submissions with your favorited "
                         "tags".format(tag.name))
    return redirect(reverse('tags:view_tag', kwargs={'tag_slug': tag.slug}))


@login_required
def list_submissions_with_favorite_tags(request, page=1):
    if request.user.profile.favorite_tags.count() == 0:
        messages.warning(request, "You must favorite some tags before you "
                         "can view this page!")
        return redirect(reverse('tags:list_tags'))

    # Filter submissions visible to the reader
    filters = filters_for_authenticated_user(request.user) if \
        request.user.is_authenticated else filters_for_anonymous_user()
    results = Submission.objects.filter(
        Q(tags__in=request.user.profile.favorite_tags.all()) & filters)
    paginator = Paginator(results, request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    return render(request, 'list_submissions_with_favorite_tags.html', {
        'title': 'Submissions with your favorite tags',
        'submissions': submissions,
    })


@login_required
@require_POST
def block_tag(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    if tag in request.user.profile.blocked_tags.all():
        messages.warning(request, "You have already blocked that tag")
    elif tag in request.user.profile.favorite_tags.all():
        messages.warning(request, "This tag is in your favorites; unfavorite "
                         "it first before blocking")
    else:
        request.user.profile.blocked_tags.add(tag)
        messages.success(request, "Tag blocked. You will no longer see "
                         "submissions tagged with {} in lists of submissions "
                         "(but will still see them if linked "
                         "directly).".format(tag.name))
    return redirect(reverse('tags:view_tag', kwargs={'tag_slug': tag.slug}))


@login_required
@require_POST
def unblock_tag(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    if tag not in request.user.profile.blocked_tags.all():
        messages.warning(request, "You haven't blocked that tag")
    else:
        request.user.profile.blocked_tags.remove(tag)
        messages.success(request, "Tag unblocked. You will now see "
                         "submissions tagged with {} in lists of "
                         "submissions".format(tag.name))
    return redirect(reverse('tags:view_tag', kwargs={'tag_slug': tag.slug}))
