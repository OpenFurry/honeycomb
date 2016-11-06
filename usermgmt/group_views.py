from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import GroupForm
from .models import FriendGroup


@login_required
def list_groups(request, username=None):
    """View for listing a user's groups.

    Args:
        username: the user whose groups to list (ignored)
    """
    return render(request, 'list_groups.html', {
        'title': 'Groups',
        'groups': request.user.profile.friend_groups.all(),
        'tab': 'social',
    })


@login_required
def create_group(request, username=None):
    """View for creating a new group.

    Args:
        username: the owner of the group (ignored)
    """
    form = GroupForm()

    # Set the members queryset to watched users
    form.fields['users'].queryset = request.user.profile.watched_users

    # Save the group if data was POSTed
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            form.save_m2m()
            request.user.profile.friend_groups.add(group)
            messages.success(request, 'Group created.')
            return redirect(reverse('usermgmt:view_group', kwargs={
                'username': request.user.username,
                'group_id': group.id,
            }))
    return render(request, 'update_group.html', {
        'title': 'Create a new group',
        'form': form,
        'tab': 'social',
    })


@login_required
def view_group(request, username=None, group_id=None):
    """View for viewing a friend group.

    Args:
        username: the owner of the group (ignored)
        group_id: the id of the group
    """
    group = get_object_or_404(FriendGroup, id=group_id)

    # Make sure the user can view the group
    if group not in request.user.profile.friend_groups.all():
        messages.error(request, 'You may not view the groups of others')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    return render(request, 'view_group.html', {
        'title': 'Viewing group "{}"'.format(group.name),
        'group': group,
        'tab': 'social',
    })


@login_required
def edit_group(request, username=None, group_id=None):
    """View for editing a friend group.

    Args:
        username: the owner of the group (ignored)
        group_id: the id of the group
    """
    group = get_object_or_404(FriendGroup, id=group_id)

    # Make sure the user can edit the group
    if group not in request.user.profile.friend_groups.all():
        messages.error(request, 'You may not edit the groups of others')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    form = GroupForm(instance=group)

    # Set the queryset for available members
    form.fields['users'].queryset = request.user.profile.watched_users

    # Update the group if data was POSTed
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            form.save_m2m()
            messages.success(request, 'Group modified.')
            return redirect(reverse('usermgmt:view_group', kwargs={
                'username': request.user.username,
                'group_id': group.id,
            }))
    return render(request, 'update_group.html', {
        'title': 'Edit group "{}"'.format(group.name),
        'form': form,
        'tab': 'social',
    })


@login_required
def delete_group(request, username=None, group_id=None):
    """View for deleting a friend group.

    Args:
        username: the owner of the group (ignored)
        group_id: the id of the group
    """
    group = get_object_or_404(FriendGroup, id=group_id)

    # Make sure that the user can delete the group
    if group not in request.user.profile.friend_groups.all():
        messages.error(request, 'You may not delete the groups of others')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)

    # Confirm deleting the group
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted.')
        return redirect(reverse('usermgmt:list_groups', kwargs={
            'username': request.user.username,
        }))
    return render(request, 'confirm_delete_group.html', {
        'title': 'Deleting group "{}"'.format(group.name),
        'group': group,
        'tab': 'social',
    })
