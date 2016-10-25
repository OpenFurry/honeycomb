from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
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
from core.templatetags.gravatar import gravatar


def view_root_level_folders(request, username=None, page=None):
    user = get_object_or_404(User, username=username)
    folders = user.folder_set.filter(parent=None)
    members = Submission.objects.filter(owner=user) \
        .annotate(Count('folderitem')) \
        .filter(folderitem__count=0)
    paginator = Paginator(members, request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except PageNotAnInteger:
        submissions = paginator.page(1)
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
                page=None):
    folder = get_object_or_404(Folder, id=folder_id)
    if username != folder.owner.username or folder_slug != folder.slug:
        return redirect(reverse('submissions:view_folder', kwargs={
            'username': folder.owner.username,
            'folder_id': folder.id,
            'folder_slug': folder.slug,
        }))
    all_folders = folder.owner.folder_set.all()
    sub_folders = filter(lambda x: x.parent == folder, all_folders)
    members = [item.submission for item in
               FolderItem.objects.filter(folder=folder)]
    paginator = Paginator(members, request.user.profile.results_per_page if
                          request.user.is_authenticated else 25)
    try:
        submissions = paginator.page(page)
    except PageNotAnInteger:
        submissions = paginator.page(1)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    title = "{} {}'s folders".format(
        gravatar(folder.owner.email, size=80),
        folder.owner.profile.get_display_name())
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
    return render(request, 'list_submissions.html', {
        'author': folder.owner,
        'submissions': submissions,
        'folders': sub_folders,
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
    folders = request.user.folder_set.all()
    form = FolderForm()
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
    folder = get_object_or_404(Folder, id=folder_id)
    if request.user != folder.owner:
        messages.error(request, "You can't update a folder that isn't yours")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied'
        }, status=403)
    folders = request.user.folder_set.exclude(id=folder.id)
    form = FolderForm(instance=folder)
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
    folder = get_object_or_404(Folder, id=folder_id)
    if request.user != folder.owner:
        messages.error(request, "You can't delete a folder that isn't yours")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied'
        }, status=403)
    if request.method == 'POST':
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
        'folder': folder,
    })


@login_required
def update_submission_order_in_folder(request, username=None, folder_id=None,
                                      folder_slug=None):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.user != folder.owner:
        messages.error(request, "You can't sort a folder that isn't yours")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied'
        }, status=403)
    if request.method == 'POST':
        position = 1
        items = FolderItem.objects.filter(folder=folder)
        for id in request.GET.getlist('ids', []):
            item = items.get(pk=id)
            item.position = position
            item.save()
            position += 1
        messages.success(request, 'Submissions sorted successfully.')
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
