from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
from django.utils import timezone

from .forms import SubmissionForm
from .models import (
    FolderItem,
    Submission,
)
from .utils import (
    filters_for_anonymous_user,
    filters_for_authenticated_user,
)
from activitystream.models import Activity
from administration.models import Flag
from core.templatetags.gravatar import gravatar
from social.forms import CommentForm
from social.models import Comment


def list_user_submissions(request, username=None, page=1):
    """View for listing all of a user's submissions.

    Args:
        username: the user whose submissions to list
        page: the current page for pagination
    """
    reader = request.user
    author = get_object_or_404(User, username=username)

    # Make sure the user can view submissions
    if reader.is_authenticated and reader in \
            author.profile.blocked_users.all():
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)

    # Get a list of submissions based on what the reader can view
    result = author.submission_set.filter(
        filters_for_authenticated_user(reader) if
        reader.is_authenticated else filters_for_anonymous_user())
    paginator = Paginator(result, reader.profile.results_per_page if
                          reader.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    display_name = '{} {}'.format(
        gravatar(author.email, size=80),
        author.profile.get_display_name())
    return render(request, 'list_submissions.html', {
        'title': "{}'s submissions".format(display_name),
        'author': author,
        'tab': 'submissions',
        'submissions': submissions,
        'url_prefix': reverse('submissions:list_user_submissions', kwargs={
            'username': author.username,
        })
    })


def list_user_favorites(request, username=None, page=1):
    """View for listing all of a user's favorited submissions.

    Args:
        username: the user whose favorited submissions to list
        page: the current page for pagination
    """
    reader = request.user
    author = get_object_or_404(User, username=username)

    # Make sure the reader can view favorites
    if reader.is_authenticated and reader in \
            author.profile.blocked_users.all():
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)

    # Get a list of submissions based on what the reader can view
    result = author.profile.favorited_submissions.filter(
        filters_for_authenticated_user(reader) if
        reader.is_authenticated else filters_for_anonymous_user())
    paginator = Paginator(result, reader.profile.results_per_page if
                          reader.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    display_name = '{} {}'.format(
        gravatar(author.email, size=80),
        author.profile.get_display_name())
    return render(request, 'list_submissions.html', {
        'title': "{}'s favorites".format(display_name),
        'author': author,
        'tab': 'favorites',
        'submissions': submissions,
        'url_prefix': reverse('submissions:list_user_favorites', kwargs={
            'username': author.username,
        })
    })


def view_submission(request, username=None, submission_id=None,
                    submission_slug=None):
    """View for displaying a submission.

    Args:
        username: the owner of the submission
        submission_id: the id of the submission
        submission_slug: the slug of the submission
    """
    # Expand short URLs.
    submission = get_object_or_404(Submission, id=submission_id)
    if username != submission.owner.username or submission_slug != \
            submission.slug:
        return redirect(reverse(
            'submissions:view_submission',
            kwargs={
                'username': submission.owner.username,
                'submission_id': submission.id,
                'submission_slug': submission.slug,
            }))

    # Fetch the submission if allowed
    reader = request.user
    author = submission.owner
    try:
        submission = Submission.objects.get(Q(id=submission_id) & (
            filters_for_authenticated_user(reader, blocked_tags=False) if
            reader.is_authenticated else filters_for_anonymous_user()))
    except Submission.DoesNotExist:
        # XXX Perhaps we should distinguish between 403 and 404 at some point
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    active_flag = submission.get_active_flag()

    # Increment the submission views
    if request.user != submission.owner:
        submission.views += 1
        submission.save()
        Activity.create('submission', 'view', submission)
        if active_flag is not None:
            can_view = False
            if request.user in active_flag.participants.all():
                can_view = True
            if not can_view and ((
                    active_flag.flag_type == Flag.SOCIAL and
                    request.user.has_perm(
                        'administration.can_view_social_flags')) or
                    (active_flag.flag_type == Flag.CONTENT and
                     request.user.has_perm(
                         'administration.can_view_content_flags'))):
                can_view = True
            if not can_view:
                return render(request, 'permission_denied.html', {
                    'title': 'Submission flagged',
                    'additional_error': 'This submission is flagged for '
                                        'administrative review.'
                }, status=403)

    display_name = '{} {}'.format(
        gravatar(author.email, size=40),
        author.profile.get_display_name())
    ctype = ContentType.objects.get_for_model(Submission)
    return render(request, 'view_submission.html', {
        'title': submission.title,
        'subtitle': 'by {}'.format(display_name),
        'submission': submission,
        'active_flag': active_flag,
        'comment_form': CommentForm(instance=Comment(
            content_type=ctype,
            object_id=submission.id)),
        'root_level_comments': Comment.objects.filter(
            content_type=ctype,
            object_id=submission.id,
            parent=None)
    })


@login_required
def edit_submission(request, username=None, submission_id=None,
                    submission_slug=None):
    """View for editing an existing submission.

    Args:
        username: the owner of the submission
        submission_id: the id of the submission
        submission_slug: the slug of the submission
    """
    submission = get_object_or_404(Submission, id=submission_id)

    # Make sure the user can edit the submission
    if submission.owner.username != request.user.username:
        messages.error(request, 'You can only edit your own submissions')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    form = SubmissionForm(instance=submission)

    # Save changes if data was POSTed
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES,
                              instance=submission)

        # Ensure files are below the max size limit
        # NB deployments should also add this to server config
        for f in request.FILES.values():
            if f.size > settings.MAX_UPLOAD_SIZE:
                form.add_error(
                    'content_file', 'Uploads must be less than {}MB'.format(
                        int(settings.MAX_UPLOAD_SIZE / (1024 * 1024))))
        if form.is_valid():
            submission = form.save(commit=False)
            submission.mtime = timezone.now()
            submission.save(update_content=True)

            # Update folder membership: add to folderes
            for folder in form.cleaned_data['folders']:
                if folder.owner == request.user:
                    try:
                        item = FolderItem.objects.get(
                            submission=submission,
                            folder=folder)
                    except FolderItem.DoesNotExist:
                        item = FolderItem(
                            submission=submission,
                            folder=folder,
                            position=len(FolderItem.objects.filter(
                                submission=submission)) + 1)
                        item.save()

            # Update folder membership: remove from folders
            for folder in submission.folders.all():
                if folder not in form.cleaned_data['folders']:
                    item = FolderItem.objects.get(
                        submission=submission,
                        folder=folder)
                    item.delete()

            # Save ManyToMany changes, minus folders, since that uses a through
            # table for managing membership
            form.cleaned_data.pop('folders')
            form.save_m2m()
            messages.success(request, 'Submission updated.')
            return redirect(reverse(
                'submissions:view_submission',
                kwargs={
                    'username': submission.owner.username,
                    'submission_id': submission_id,
                    'submission_slug': submission.slug,
                }))

    # Set default querysets for folders and groups
    form.fields['folders'].queryset = request.user.folder_set.all()
    form.fields['allowed_groups'].queryset = \
        request.user.profile.friend_groups.all()
    return render(request, 'edit_submission.html', {
        'title': 'Edit submission',
        'form': form,
        'max_upload_size': settings.MAX_UPLOAD_SIZE,
    })


@login_required
def delete_submission(request, username=None, submission_id=None,
                      submission_slug=None):
    """View for deleting a submission.

    Args:
        username: the owner of the submission
        submission_id: the id of the submission
        submission_slug: the slug of the submission
    """
    submission = get_object_or_404(Submission, id=submission_id)

    # Make sure the user can delete the submission
    if submission.owner.username != request.user.username:
        messages.error(request, 'You can only delete your own submissions')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)

    # Confirm submission deletion
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Submission deleted.')
        return redirect(reverse('usermgmt:view_profile',
                        args=(request.user.username,)))
    return render(request, 'confirm_delete_submission.html', {
        'title': 'Deleting submission "{}"'.format(submission.title),
        'submission': submission,
    })


@login_required
def submit(request):
    """View for submitting a new submission."""
    form = SubmissionForm()

    # Create submission if data was POSTed
    if request.method == 'POST':
        # Check filesize against max
        # NB this should also be done per deployment in server config
        form = SubmissionForm(request.POST, request.FILES)
        for f in request.FILES.values():
            if f.size > settings.MAX_UPLOAD_SIZE:
                form.add_error(
                    'content_file', 'Uploads must be less than {}MB'.format(
                        int(settings.MAX_UPLOAD_SIZE / (1024 * 1024))))
        if form.is_valid():
            submission = form.save(commit=False)
            submission.ctime = timezone.now()
            submission.owner = request.user
            submission.save(update_content=True)

            # Set folder memberships
            for folder in form.cleaned_data['folders']:
                if folder.owner == request.user:
                    item = FolderItem(
                        submission=submission,
                        folder=folder,
                        position=len(FolderItem.objects.filter(
                            submission=submission)) + 1)
                    item.save()

            # Save ManyToMany data, minus folders which use a through table
            form.cleaned_data.pop('folders')
            form.save_m2m()
            messages.success(request, 'Submission created.')
            return redirect(reverse(
                'submissions:view_submission',
                kwargs={
                    'username': submission.owner.username,
                    'submission_id': submission.id,
                    'submission_slug': submission.slug,
                }))

    # Set default querysets for folders and groups
    form.fields['folders'].queryset = request.user.folder_set.all()
    form.fields['allowed_groups'].queryset = \
        request.user.profile.friend_groups.all()
    return render(request, 'edit_submission.html', {
        'title': 'Create submission',
        'form': form,
        'max_upload_size': settings.MAX_UPLOAD_SIZE,
    })
