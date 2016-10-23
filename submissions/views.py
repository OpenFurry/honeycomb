from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
)
from django.core.urlresolvers import reverse
from django.db.models import (
    Q,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import SubmissionForm
from .models import Submission
from core.templatetags.gravatar import gravatar


def list_user_submissions(request, username=None, page=None):
    reader = request.user
    author = get_object_or_404(User, username=username)
    if reader.is_authenticated and reader in \
            author.profile.blocked_users.all():
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    queries = [Q(owner=author)]
    if reader != author:
        queries.append(Q(hidden=False))
        if (not reader.is_authenticated or
                not reader.profile.can_see_adult_submissions):
            queries.append(Q(adult_rating=False))
        group_queries = []
        for group in author.groups.all():
            group_queries.append(Q(user_group__contains=group))
        if len(group_queries) > 0:
            queries.append(
                Q(restricted_to_groups=False) |
                (Q(restricted_to_groups=True), group_queries))
        else:
            queries.append(Q(restricted_to_groups=False))
    result = Submission.objects.filter(*queries)
    paginator = Paginator(result, reader.profile.results_per_page if
                          reader.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except PageNotAnInteger:
        submissions = paginator.page(1)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    display_name = '{} {}'.format(
        gravatar(author.email, size=80),
        author.profile.get_display_name())
    return render(request, 'list_submissions.html',
                  {
                      'title': "{}'s submissions".format(display_name),
                      'author': author,
                      'submissions': submissions,
                  })


def view_submission(request, username=None, submission_id=None,
                    submission_slug=None):
    submission = get_object_or_404(Submission, id=submission_id)
    # Expand short URLs.
    if username != submission.owner.username or submission_slug != \
            submission.slug:
        return redirect(reverse(
            'submissions:view_submission',
            kwargs={
                'username': submission.owner.username,
                'submission_id': submission.id,
                'submission_slug': submission.slug,
            }))
    # Check permissions
    reader = request.user
    author = submission.owner
    can_view = True
    logged_in = reader.is_authenticated
    if (logged_in and reader in author.profile.blocked_users.all()):
        can_view = False
    if can_view and reader != author:
        if submission.adult_rating and (
                not logged_in or not
                reader.profile.can_see_adult_submissions):
            can_view = False
        if can_view and submission.hidden:
            can_view = False
        if can_view and (not logged_in and submission.restricted_to_groups):
            can_view = False
        if can_view and (logged_in and submission.restricted_to_groups):
            group_allowed = False
            submission_group_ids = map(lambda x: x.id,
                                       submission.allowed_groups.all())
            user_group_ids = map(lambda x: x.id, request.user.group_set.all())
            for user_group in user_group_ids:
                if user_group in submission_group_ids:
                    group_allowed = True
                    break
            can_view = can_view and group_allowed
    if not can_view:
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    submission.views += 1
    submission.save()
    display_name = '{} {}'.format(
        gravatar(author.email, size=40),
        author.profile.get_display_name())
    return render(request, 'view_submission.html', {
        'title': submission.title,
        'subtitle': 'by {}'.format(display_name),
        'submission': submission,
    })


@login_required
def edit_submission(request, username=None, submission_id=None,
                    submission_slug=None):
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.owner.username != request.user.username:
        messages.error(request, 'You can only edit your own submissions')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        submission = form.save()
        messages.success(request, 'Submission updated.')
        return redirect(reverse(
            'submissions:view_submission',
            kwargs={
                'username': submission.owner.username,
                'submission_id': submission_id,
                'submission_slug': submission.slug,
            }))
    form = SubmissionForm(instance=submission)
    return render(request, 'edit_submission.html', {
        'title': 'Edit submission',
        'form': form,
    })


@login_required
def delete_submission(request, username=None, submission_id=None,
                      submission_slug=None):
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.owner.username != request.user.username:
        messages.error(request, 'You can only delete your own submissions')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Submission deleted.')
        return redirect(reverse('usermgmt:view_profile',
                        args=(request.user.username,)))
    return render(request, 'confirm_delete_submission.html', {
        'submission': submission,
    })


@login_required
def submit(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        submission = form.save(commit=False)
        submission.owner = request.user
        submission.save()
        messages.success(request, 'Submission created.')
        return redirect(reverse(
            'submissions:view_submission',
            kwargs={
                'username': submission.owner.username,
                'submission_id': submission.id,
                'submission_slug': submission.slug,
            }))
    form = SubmissionForm()
    return render(request, 'edit_submission.html', {
        'title': 'Create submission',
        'form': form,
    })
