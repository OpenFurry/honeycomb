from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import (
    EmptyPage,
    Paginator,
)
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from .models import Rating
from activitystream.models import Activity
from submissions.models import Submission
from usermgmt.models import Notification


@login_required
@require_POST
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
        notification = Notification(
            target=user,
            source=request.user,
            notification_type=Notification.WATCH)
        notification.save()
        Activity.create('social', 'watch', request.user)
    return redirect(reverse('usermgmt:view_profile', args=(user.username,)))


@login_required
@require_POST
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
        possible_notifications = Notification.objects.filter(
                target=user,
                source=request.user,
                notification_type=Notification.WATCH)
        if len(possible_notifications) > 0:
            for notification in possible_notifications:
                notification.delete()
        Activity.create('social', 'unwatch', request.user)
    return redirect(reverse('usermgmt:view_profile', args=(user.username,)))


@login_required
@require_POST
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
        Activity.create('social', 'block', request.user)
    return redirect(reverse('usermgmt:view_profile', args=(user.username,)))


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
            Activity.create('social', 'unblock', request.user)
        else:
            return render(request, 'confirm_unblock_user.html',
                          {'blocked_user': user})
    return redirect(reverse('usermgmt:view_profile', args=(user.username,)))


@login_required
def message_user(request, username):
    pass


@login_required
@require_POST
def favorite_submission(request, username=None, submission_id=None,
                        submission_slug=None):
    submission = get_object_or_404(Submission, id=submission_id)
    reader = request.user
    author = submission.owner
    if reader == author:
        messages.warning(request, "You cannot favorite your own submission.")
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    if reader in author.profile.blocked_users.all():
        messages.error(request, "You cannot favorite this submission, as you "
                       "have been blocked by the author.")
        return render(request, 'permission_denied.html', {}, status=403)
    if submission in reader.profile.favorited_submissions.all():
        messages.warning(request, "You have already favorited this "
                         "submission")
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    reader.profile.favorited_submissions.add(submission)
    messages.success(request, "Submission favorited!")
    notification = Notification(
        target=author,
        source=reader,
        notification_type=Notification.FAVORITE,
        subject=submission)
    notification.save()
    Activity.create('social', 'favorite', submission)
    return redirect(reverse('submissions:view_submission',
                    kwargs={
                        'username': username,
                        'submission_id': submission_id,
                        'submission_slug': submission_slug,
                    }))


@login_required
@require_POST
def unfavorite_submission(request, username=None, submission_id=None,
                          submission_slug=None):
    submission = get_object_or_404(Submission, id=submission_id)
    reader = request.user
    author = submission.owner
    if reader == author:
        messages.warning(request, "You cannot unfavorite your own "
                         "submission.")
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    if reader in author.profile.blocked_users.all():
        messages.error(request, "You cannot unfavorite this submission, as "
                       "you have been blocked by the author.")
        return render(request, 'permission_denied.html', {}, status=403)
    if submission not in reader.profile.favorited_submissions.all():
        messages.warning(request, "You haven't yet favorited this "
                         "submission")
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    reader.profile.favorited_submissions.remove(submission)
    messages.info(request, "Submission removed from favorites.")
    possible_notifications = Notification.objects.filter(
        target=author,
        source=reader,
        notification_type=Notification.FAVORITE,
        subject_id=submission_id)
    if len(possible_notifications) > 0:
        for notification in possible_notifications:
            notification.delete()
    Activity.create('social', 'unfavorite', submission)
    return redirect(reverse('submissions:view_submission',
                    kwargs={
                        'username': username,
                        'submission_id': submission_id,
                        'submission_slug': submission_slug,
                    }))


@login_required
@require_POST
def rate_submission(request, username=None, submission_id=None,
                    submission_slug=None):
    submission = get_object_or_404(Submission, id=submission_id)
    reader = request.user
    author = submission.owner
    try:
        rating = int(request.POST.get('rating', 0))
    except ValueError:
        rating = 0
    if rating not in range(1, 6):
        messages.error(request, 'Invalid rating specified.')
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    if reader == author:
        messages.warning(request, "You cannot rate your own submission.")
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    if reader in author.profile.blocked_users.all():
        messages.error(request, "You cannot rate this submission, as "
                       "you have been blocked by the author.")
        return render(request, 'permission_denied.html', {}, status=403)
    try:
        rating_object = Rating.objects.get(
            owner=reader,
            submission=submission,
        )
        rating_object.rating = rating
        rating_object.save()
        messages.success(request, "Existing rating updated.")
    except Rating.DoesNotExist:
        rating_object = Rating(
            owner=reader,
            submission=submission,
            rating=rating,
        )
        rating_object.save()
        messages.success(request, "Submission successfully rated.")
    notification = Notification(
        target=author,
        source=reader,
        notification_type=Notification.RATING,
        subject=rating_object)
    notification.save()
    ratings = submission.get_average_rating()
    submission.rating_stars = ratings['stars']
    submission.rating_average = ratings['average']
    submission.rating_count = ratings['count']
    submission.save()
    Activity.create('social', 'rate', rating_object)
    return redirect(reverse('submissions:view_submission',
                    kwargs={
                        'username': username,
                        'submission_id': submission_id,
                        'submission_slug': submission_slug,
                    }))


@login_required
@require_POST
def enjoy_submission(request, username=None, submission_id=None,
                     submission_slug=None):
    submission = get_object_or_404(Submission, id=submission_id)
    reader = request.user
    author = submission.owner
    if reader == author:
        messages.warning(request, "You cannot add enjoy votes to your own "
                         "submission.")
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    if reader in author.profile.blocked_users.all():
        messages.error(request, "You cannot add enjoy votes to this "
                       "submission, as you have been blocked by the author.")
        return render(request, 'permission_denied.html', {}, status=403)
    if not submission.can_enjoy:
        messages.error(request, 'The author has disabled enjoy voting on '
                       'this submission.')
        return redirect(reverse('submissions:view_submission',
                        kwargs={
                            'username': username,
                            'submission_id': submission_id,
                            'submission_slug': submission_slug,
                        }))
    submission.enjoy_votes += 1
    submission.save()
    messages.success(request, "Enjoy vote added to submission!")
    notification = Notification(
        target=author,
        source=reader,
        notification_type=Notification.ENJOY,
        subject=submission)
    notification.save()
    Activity.create('social', 'enjoy', submission)
    return redirect(reverse('submissions:view_submission',
                    kwargs={
                        'username': username,
                        'submission_id': submission_id,
                        'submission_slug': submission_slug,
                    }))


@login_required
def view_notifications_ab(request):
    view = 'categories' if request.user.id % 2 == 0 else 'timeline'
    return redirect(reverse('social:view_notifications_{}'.format(view)))


@login_required
def view_notifications_categories(request):
    return render(request, 'notifications_categories.html', {
        'title': 'Notifications',
        'notifications': request.user.profile.get_notifications_sorted(),
    })


@login_required
def view_notifications_timeline(request, page=1):
    paginator = Paginator(request.user.notification_set.all(), 50)
    try:
        notifications = paginator.page(page)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)
    return render(request, 'notifications_timeline.html', {
        'title': 'Notifications',
        'notifications': notifications,
    })


@login_required
@require_POST
def remove_notifications(request):
    for notification_id in request.POST.getlist('notification_id', []):
        try:
            notification = Notification.objects.get(pk=notification_id)
            if notification.target == request.user:
                notification.delete()
            else:
                messages.error(request, 'One or more of the notifications '
                               'you attempted to delete does not belong to '
                               'you.  Some notifications may have been '
                               'deleted successfully, however.')
                return render(request, 'permission_denied.html', {
                    'title': 'Permission denied',
                }, status=403)
        except Notification.DoesNotExist:
            continue
    messages.success(request, 'Notifications deleted.')
    return redirect(reverse('social:view_notifications'))


@login_required
@require_POST
def nuke_notifications(request):
    notifications = Notification.objects.filter(target=request.user)
    for notification in notifications:
        notification.delete()
    request.user.profile.expired_notifications = 0
    request.user.profile.save()
    messages.success(request, 'All notifications nuked.')
    return redirect(reverse('social:view_notifications'))
