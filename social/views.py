from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)


@login_required
def watch_user(request, username):
    user = get_object_or_404(User, username=username)
    if user.username == request.user.username:
        messages.warning(request, "You can't watch yourself.")
    elif user in request.user.profile.watched_users.all():
        messages.info(request, "You are already watching this user.")
    else:
        request.user.profile.watched_users.add(user)
        request.user.profile.save()
        messages.success(request,
                         "You are now watching {}!".format(user.username))
    return redirect(reverse('view_profile', args=(user.username,)))


@login_required
def unwatch_user(request, username):
    user = get_object_or_404(User, username=username)
    if user.username == request.user.username:
        messages.warning(request, "You can't unwatch yourself.")
    elif user not in request.user.profile.watched_users.all():
        messages.info(request, "You are not watching this user.")
    else:
        request.user.profile.watched_users.remove(user)
        request.user.profile.save()
        messages.success(request,
                         "You are no longer watching {}.".format(
                             user.username))
    return redirect(reverse('view_profile', args=(user.username,)))


@login_required
def block_user(request, username):
    user = get_object_or_404(User, username=username)
    if user.username == request.user.username:
        messages.warning(request, "You can't block yourself.")
    elif user in request.user.profile.blocked_users.all():
        messages.info(request, "You are already blocking this user.")
    else:
        request.user.profile.blocked_users.add(user)
        request.user.profile.save()
        messages.success(
            request,
            ("You are now blocking {} from viewing your profile and "
             "submissions!").format(user.username))
    return redirect(reverse('view_profile', args=(user.username,)))


@login_required
def unblock_user(request, username):
    user = get_object_or_404(User, username=username)
    if user.username == request.user.username:
        messages.warning(request, "You can't unblock yourself.")
    elif user not in request.user.profile.blocked_users.all():
        messages.info(request, "You are not blocking this user.")
    else:
        if request.method == 'POST':
            request.user.profile.blocked_users.remove(user)
            request.user.profile.save()
            messages.success(
                request,
                ("You are no longer blocking {} from viewing your profile and "
                 "submissions.").format(user.username))
        else:
            return render(request, 'confirm_unblock_user.html',
                          {'blocked_user': user})
    return redirect(reverse('view_profile', args=(user.username,)))


@login_required
def message_user(request, username):
    pass
