from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import (
    EmptyPage,
    Paginator,
)
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import FolderForm
from .models import (
    Folder,
    FolderItem,
    Submission,
)
from activitystream.models import Activity
from core.templatetags.gravatar import gravatar


def view_root_level_folders(request, username=None, page=1):
    """View for listing folders at the root level, as well as submissions not
    placed in any folders.
    """
    # TODO Filter submission visibility
    # @makyo 2016-11-06 #60
    user = get_object_or_404(User, username=username)

    # Get all folders with no parents
    folders = user.folder_set.filter(parent=None)

    # Get all submissions with no attached folder items
    members = Submission.objects.filter(owner=user) \
        .annotate(Count('folderitem')) \
        .filter(folderitem__count=0)
    paginator = Paginator(members, request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    title = "{} {}'s folders".format(
        gravatar(user.email, size=80),
        user.profile.get_display_name())
    return render(request, 'list_submissions.html', {
        'author': user,
        'submissions': submissions,
        'folders': folders,
        'title': title,
        'tab': 'folders',
        'subtitle': '/',
        'url_prefix': reverse('submissions:view_root_level_folders', kwargs={
            'username': user.username,
        }),
    })


def view_folder(request, username=None, folder_id=None, folder_slug=None,
                page=1):
    """View for listing subfolders and submissions within a folder.

    Args:
        username: the owner of the folder
        folder_id: the id of the folder
        folder_slug: the slug of the folder
    """
    # TODO Filter submission visibility
    # @makyo 2016-11-06 #60

    # Expand short urls
    folder = get_object_or_404(Folder, id=folder_id)
    if username != folder.owner.username or folder_slug != folder.slug:
        return redirect(reverse('submissions:view_folder', kwargs={
            'username': folder.owner.username,
            'folder_id': folder.id,
            'folder_slug': folder.slug,
        }))

    # Get subfolders
    subfolders = folder.owner.folder_set.filter(parent=folder)

    # Get submissions in this folder
    # (See above TODO)
    members = [item.submission for item in
               FolderItem.objects.filter(folder=folder)]
    paginator = Paginator(members, request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    title = "{} {}'s folders".format(
        gravatar(folder.owner.email, size=80),
        folder.owner.profile.get_display_name())

    # Build breadcrumbs for this folder
    breadcrumbs = ['<em>{}</em>'.format(folder.name)]
    curr = folder.parent
    while curr is not None:
        breadcrumbs.append('<a href="{}"><em>{}</em></a>'.format(
            reverse('submissions:view_folder', kwargs={
                'username': folder.owner.username,
                'folder_id': curr.id,
                'folder_slug': curr.slug,
            }),
            curr.name,
        ))
        curr = curr.parent
    breadcrumbs.reverse()
    path = '/'.join(breadcrumbs)
    Activity.create('folder', 'view', folder)
    return render(request, 'list_submissions.html', {
        'author': folder.owner,
        'submissions': submissions,
        'folders': subfolders,
        'folder': folder,
        'title': title,
        'tab': 'folders',
        'subtitle': '/{}'.format(path),
        'url_prefix': reverse('submissions:view_folder', kwargs={
            'username': folder.owner.username,
            'folder_id': folder.id,
            'folder_slug': folder.slug,
        }),
    })


@login_required
def create_folder(request, username=None):
    """View for creating a folder.

    Args:
        username: the owner of the folder (ignored)
    """
    folders = request.user.folder_set.all()
    form = FolderForm()

    # Create the folder if data was POSTed
    if request.method == 'POST':
        form = FolderForm(request.POST)
        folder = form.save(commit=False)
        folder.owner = request.user
        folder.save()
        return redirect(reverse('submissions:view_folder', kwargs={
            'username': folder.owner.username,
            'folder_id': folder.id,
            'folder_slug': folder.slug,
        }))
    form.fields['parent'].queryset = folders
    return render(request, 'edit_folder.html', {
        'form': form,
        'title': 'Create folder',
    })


@login_required
def update_folder(request, username=None, folder_id=None, folder_slug=None):
    """View for updating a folder.

    Args:
        username: the owner of the folder
        folder_id: the id of the folder
        folder_slug: the slug of the folder
    """
    folder = get_object_or_404(Folder, id=folder_id)

    # Ensure that the user can update the folder
    if request.user != folder.owner:
        messages.error(request, "You can't update a folder that isn't yours")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied'
        }, status=403)

    # Get all other folders for the user for setting as the parent
    folders = request.user.folder_set.exclude(id=folder.id)
    form = FolderForm(instance=folder)

    # Update the folder if data was POSTed
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        folder = form.save(commit=False)
        folder.owner = request.user
        folder.save()
        return redirect(reverse('submissions:view_folder', kwargs={
            'username': folder.owner.username,
            'folder_id': folder.id,
            'folder_slug': folder.slug,
        }))
    form.fields['parent'].queryset = folders
    return render(request, 'edit_folder.html', {
        'form': form,
        'title': 'Update folder',
    })


@login_required
def delete_folder(request, username=None, folder_id=None, folder_slug=None):
    """View for deleting a folder.

    Args:
        username: the owner of the folder
        folder_id: the id of the folder
        folder_slug: the slug of the folder
    """
    folder = get_object_or_404(Folder, id=folder_id)

    # Make sure the user can delete the folder
    if request.user != folder.owner:
        messages.error(request, "You can't delete a folder that isn't yours")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied'
        }, status=403)

    # Confirm deleting the folder
    if request.method == 'POST':
        # Pick a valid redirect URL based on the current folder's parent
        if folder.parent:
            next_url = reverse('submissions:view_folder', kwargs={
                'username': request.user.username,
                'folder_id': folder.parent.id,
                'folder_slug': folder.parent.slug,
            })
        else:
            next_url = reverse('submissions:view_root_level_folders', kwargs={
                'username': request.user.username
            })
        folder.delete()
        messages.success(request, 'Folder deleted successfully.')
        return redirect(next_url)
    return render(request, 'confirm_delete_folder.html', {
        'title': 'Deleting folder "{}"'.format(folder.name),
        'folder': folder,
    })


@login_required
def update_submission_order_in_folder(request, username=None, folder_id=None,
                                      folder_slug=None):
    """View for re-ordering submissions in a folder.

    Args:
        username: the owner of the folder
        folder_id: the id of the folder
        folder_slug: the slug of the folder
    """
    folder = get_object_or_404(Folder, id=folder_id)

    # Make sure the user can update the folder
    if request.user != folder.owner:
        messages.error(request, "You can't sort a folder that isn't yours")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied'
        }, status=403)

    # Save the updated order if data was POSTed
    if request.method == 'POST':
        position = 1
        items = FolderItem.objects.filter(folder=folder)
        # Update the folder items' positions based on input
        for id in request.GET.getlist('ids', []):
            item = items.get(pk=id)
            item.position = position
            item.save()
            position += 1
        messages.success(request, 'Submissions sorted successfully.')
        Activity.create('folder', 'sort', folder)

    # Generate breadcrumbs for the folder
    breadcrumbs = ['<em>{}</em>'.format(folder.name)]
    curr = folder.parent
    while curr is not None:
        breadcrumbs.append('<a href="{}"><em>{}</em></a>'.format(
            reverse('submissions:view_folder', kwargs={
                'username': folder.owner.username,
                'folder_id': curr.id,
                'folder_slug': curr.slug,
            }),
            curr.name,
        ))
        curr = curr.parent
    breadcrumbs.reverse()
    path = '/'.join(breadcrumbs)
    return render(request, 'update_submission_order_in_folder.html', {
        'folder': folder,
        'title': 'Sort folder items',
        'subtitle': '/{}'.format(path),
        'folder_items': FolderItem.objects.filter(folder=folder),
    })
