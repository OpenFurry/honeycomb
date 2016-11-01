import pypandoc
import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
from core.templatetags.gravatar import gravatar


def list_user_submissions(request, username=None, page=1):
    reader = request.user
    author = get_object_or_404(User, username=username)
    if reader.is_authenticated and reader in \
            author.profile.blocked_users.all():
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
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
    reader = request.user
    author = get_object_or_404(User, username=username)
    if reader.is_authenticated and reader in \
            author.profile.blocked_users.all():
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
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
            filters_for_authenticated_user(reader) if
            reader.is_authenticated else filters_for_anonymous_user()))
    except Submission.DoesNotExist:
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    submission.views += 1
    submission.save()
    Activity.create('submission', 'view', submission)
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
    form = SubmissionForm(instance=submission)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        uploaded_data = None
        for f in request.FILES.values():
            if f.size > settings.MAX_UPLOAD_SIZE:
                form.add_error(
                    'content_file', 'Uploads must be less than {}MB'.format(
                        settings.MAX_UPLOAD_SIZE / (1024 * 1024)))
        if ('content_file' in request.FILES
                and 'content_file' not in form.errors):
            f = request.FILES['content_file']
            with tempfile.NamedTemporaryFile(suffix='.{}'.format(
                    f.name.split('.')[-1])) as temp:
                for chunk in f.chunks():
                    temp.write(chunk)
                temp.flush()
                uploaded_data = pypandoc.convert_file(
                    temp.name, 'md')
        if form.is_valid():
            submission = form.save(commit=False)
            submission.mtime = timezone.now()
            if uploaded_data is not None:
                submission.content_raw = uploaded_data
            submission.save()
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
            for folder in submission.folders.all():
                if folder not in form.cleaned_data['folders']:
                    item = FolderItem.objects.get(
                        submission=submission,
                        folder=folder)
                    item.delete()
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
        'title': 'Deleting submission "{}"'.format(submission.title),
        'submission': submission,
    })


@login_required
def submit(request):
    form = SubmissionForm()
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        uploaded_data = None
        for f in request.FILES.values():
            if f.size > settings.MAX_UPLOAD_SIZE:
                form.add_error(
                    'content_file', 'Uploads must be less than {}MB'.format(
                        settings.MAX_UPLOAD_SIZE / (1024 * 1024)))
        if 'content_file' in request.FILES:
            f = request.FILES['content_file']
            with tempfile.NamedTemporaryFile(suffix='.{}'.format(
                    f.name.split('.')[-1])) as temp:
                for chunk in f.chunks():
                    temp.write(chunk)
                temp.flush()
                uploaded_data = pypandoc.convert_file(
                    temp.name, 'md')
        if form.is_valid():
            submission = form.save(commit=False)
            submission.owner = request.user
            if uploaded_data is not None:
                submission.content_raw = uploaded_data
            submission.save()
            for folder in form.cleaned_data['folders']:
                if folder.owner == request.user:
                    item = FolderItem(
                        submission=submission,
                        folder=folder,
                        position=len(FolderItem.objects.filter(
                            submission=submission)) + 1)
                    item.save()
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
    form.fields['folders'].queryset = request.user.folder_set.all()
    form.fields['allowed_groups'].queryset = \
        request.user.profile.friend_groups.all()
    return render(request, 'edit_submission.html', {
        'title': 'Create submission',
        'form': form,
        'max_upload_size': settings.MAX_UPLOAD_SIZE,
    })
