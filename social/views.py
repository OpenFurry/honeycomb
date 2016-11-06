from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
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

from .forms import CommentForm
from .models import (
    Comment,
    Rating,
)
from activitystream.models import Activity
from submissions.models import Submission
from usermgmt.models import Notification


@login_required
@require_POST
def watch_user(request, username):
    """View for watching a user.

    Args:
        username: the user to watch
    """
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
    """View for unwatching a user.

    Args:
        username: the user to unwatch
    """
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
    """View for blocking a user.

    Args:
        username: the user to block
    """
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
    """View to unblock a user.

    Args:
        username: the user to unblock
    """
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
    """View to message a user."""
    pass


@login_required
@require_POST
def favorite_submission(request, username=None, submission_id=None,
                        submission_slug=None):
    """View to favorite a submission.

    Args:
        username: the owner of the submission
        submission_id: the id of the submission
        submission_slug: the slug of the submission
    """
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
    """View to unfavorite a submission.

    Args:
        username: the owner of the submission
        submission_id: the id of the submission
        submission_slug: the slug of the submission
    """
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
    """View to rate a submission.

    Args:
        request: Django request object; `rating` should be in request.POST
        username: the owner of the submission
        submission_id: the id of the submission
        submission_slug: the slug of the submission
    """
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
    """View for adding an enjoy vote to a submission

    Args:
        username: the owner of the submission
        submission_id: the id of the submission
        submission_slug: the slug of the submission
    """
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
@require_POST
def post_comment(request):
    """View for posting a comment on a model."""
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        if comment.object_model.can_comment:
            comment.owner = request.user
            comment.target_object_owner = comment.object_model.owner
            comment.save()
            form.save_m2m()

            # Notify the object owner that their object has received
            # a comment if it's not them making the comment.
            if (isinstance(comment.object_model, Submission)
                    and request.user != comment.object_model.owner):
                Notification(
                    notification_type=Notification.SUBMISSION_COMMENT,
                    target=comment.target_object_owner,
                    source=request.user,
                    subject=comment).save()

            # If the comment is a reply to another comment, notify all parent
            # comments that their comment has received a comment reply, so
            # long as the parent comment owner is not the one making the reply.
            if comment.parent:
                c = comment
                while c.parent is not None:
                    if request.user != c.parent.owner:
                        Notification(
                            notification_type=Notification.COMMENT_REPLY,
                            target=c.parent.owner,
                            source=request.user,
                            subject=comment).save()
                    c = c.parent
            return redirect(comment.get_absolute_url())
    messages.error(request, "There was an error posting that comment")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def delete_comment(request):
    """View for deleting a comment."""
    # TODO: deleting should wipe content, flagging should leave it.
    # @makyo 2016-11-05 #57
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if not comment.deleted:
        if request.user == comment.owner:
            comment.deleted = True
            comment.deleted_by_object_owner = False
            comment.save()
            messages.success(request, "Comment deleted.")
        elif request.user == comment.target_object_owner:
            comment.deleted = True
            comment.deleted_by_object_owner = True
            comment.save()
            messages.success(request, "Comment deleted.")
        else:
            messages.error(request, "You may only delete a comment if you are "
                           "the poster or the page owner.")

    # Delete any outstanding notifications
    if comment.deleted:
        ctype = ContentType.objects.get(app_label='social', model='comment')
        possible_notifications = Notification.objects.filter(
            subject_content_type=ctype,
            subject_id=comment.id)
        for notification in possible_notifications:
            notification.delete()

        # As we don't rely on existing signals, create our own activity stream
        # item refering to this comment.
        Activity.create('comment', 'delete', comment)
    return redirect(comment.object_model.get_absolute_url())


@login_required
def view_notifications_ab(request):
    """View for choosing whether a user sees timeline or category style
    notifications
    """
    view = 'categories' if request.user.id % 2 == 0 else 'timeline'
    return redirect(reverse('social:view_notifications_{}'.format(view)))


@login_required
def view_notifications_categories(request):
    """View for seeing notifications in category style."""
    return render(request, 'notifications_categories.html', {
        'title': 'Notifications',
        'notifications': request.user.profile.get_notifications_sorted(),
    })


@login_required
def view_notifications_timeline(request, page=1):
    """View for seeing notifications in timeline style."""
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
    """View for removing selected notifications."""
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
    """View for removing all notifications."""
    notifications = Notification.objects.filter(target=request.user)
    for notification in notifications:
        notification.delete()
    request.user.profile.expired_notifications = 0
    request.user.profile.save()
    messages.success(request, 'All notifications nuked.')
    return redirect(reverse('social:view_notifications'))
