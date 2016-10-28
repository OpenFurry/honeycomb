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
    return render(request, 'list_groups.html', {
        'title': 'Groups',
        'groups': request.user.profile.friend_groups.all(),
        'tab': 'social',
    })


@login_required
def create_group(request, username=None):
    form = GroupForm()
    form.fields['members'].queryset = request.user.profile.watched_users
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            for user in form.cleaned_data['members']:
                group.users.add(user)
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
    group = get_object_or_404(FriendGroup, id=group_id)
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
    group = get_object_or_404(FriendGroup, id=group_id)
    if group not in request.user.profile.friend_groups.all():
        messages.error(request, 'You may not edit the groups of others')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    form = GroupForm(instance=group)
    form.fields['members'].queryset = request.user.profile.watched_users
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            for user in form.cleaned_data['members']:
                if user not in group.users.all():
                    group.users.add(user)
            for user in group.users.all():
                if user not in form.cleaned_data['members']:
                    group.users.remove(user)
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
    group = get_object_or_404(FriendGroup, id=group_id)
    if group not in request.user.profile.friend_groups.all():
        messages.error(request, 'You may not delete the groups of others')
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
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
