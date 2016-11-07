from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from .models import (
    Comment,
    Rating,
)
from administration.models import Application
from submissions.models import Submission
from usermgmt.models import (
    Notification,
    Profile,
)


class BaseSocialViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.foo = User.objects.create_user('foo', 'foo@example.com',
                                           'a good password')
        cls.foo.profile = Profile(profile_raw='Wow!',
                                  display_name='Mx Foo Bar')
        cls.foo.profile.save()
        cls.bar = User.objects.create_user('bar', 'bar@example.com',
                                           'another good password')
        cls.bar.profile = Profile(profile_raw='Whoa', display_name='Bad Wolf')
        cls.bar.profile.save()


class TestWatchUserView(BaseSocialViewTestCase):
    def test_user_watched(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:watch_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, "You are now watching bar!")
        self.assertIn(self.bar, self.foo.profile.watched_users.all())
        notification = Notification.objects.get(pk=1)
        self.assertEqual(notification.notification_type, Notification.WATCH)

    def test_cant_watch_self(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:watch_user',
                                    args=('foo',)),
                                    follow=True)
        self.assertContains(response, "watch yourself.")

    def test_already_watched(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.watched_users.add(self.bar)
        response = self.client.post(reverse('social:watch_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, 'You are already watching this user.')

    def test_404(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:watch_user',
                                    args=('bad-wolf',)),
                                    follow=True)
        self.assertEqual(response.status_code, 404)


class TestUnwatchUserView(BaseSocialViewTestCase):
    def test_user_unwatched(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.watched_users.add(self.bar)
        response = self.client.post(reverse('social:unwatch_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, "You are no longer watching bar.")
        self.assertNotIn(self.bar, self.foo.profile.watched_users.all())

    def test_notification_removed(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.watched_users.add(self.bar)
        notification = Notification(
            target=self.bar,
            source=self.foo,
            notification_type=Notification.WATCH)
        notification.save()
        response = self.client.post(reverse('social:unwatch_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, "You are no longer watching bar.")
        self.assertNotIn(self.bar, self.foo.profile.watched_users.all())
        with self.assertRaises(Notification.DoesNotExist):
            notification.refresh_from_db()

    def test_cant_unwatch_self(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:unwatch_user',
                                    args=('foo',)),
                                    follow=True)
        self.assertContains(response, "unwatch yourself.")

    def test_not_watching(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:unwatch_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, 'You are not watching this user.')

    def test_404(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:unwatch_user',
                                    args=('bad-wolf',)),
                                    follow=True)
        self.assertEqual(response.status_code, 404)


class TestBlockUserView(BaseSocialViewTestCase):
    def test_user_blocked(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:block_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, 'You are now blocking bar from viewing '
                            'your profile and submissions!')
        self.assertIn(self.bar, self.foo.profile.blocked_users.all())

    def test_cant_block_self(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:block_user',
                                    args=('foo',)),
                                    follow=True)
        self.assertContains(response, "block yourself.")

    def test_already_blocked(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.blocked_users.add(self.bar)
        response = self.client.post(reverse('social:block_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, 'You are already blocking this user.')

    def test_404(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(reverse('social:block_user',
                                    args=('bad-wolf',)),
                                    follow=True)
        self.assertEqual(response.status_code, 404)


class TestUnblockUserView(BaseSocialViewTestCase):
    def test_user_unblocked(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.blocked_users.add(self.bar)
        response = self.client.get(reverse('social:unblock_user',
                                   args=('bar',)),
                                   follow=True)
        self.assertContains(response, 'Are you sure that you want to do this?')
        response = self.client.post(reverse('social:unblock_user',
                                    args=('bar',)),
                                    follow=True)
        self.assertContains(response, 'You are no longer blocking bar')

    def test_cant_unblock_self(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:unblock_user',
                                   args=('foo',)),
                                   follow=True)
        self.assertContains(response, "unblock yourself.")

    def test_not_blocking(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:unblock_user',
                                   args=('bar',)),
                                   follow=True)
        self.assertContains(response, 'You are not blocking this user.')

    def test_404(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:unblock_user',
                                   args=('bad-wolf',)),
                                   follow=True)
        self.assertEqual(response.status_code, 404)


class TestMessageUserView(BaseSocialViewTestCase):
    pass


class BaseSocialSubmissionViewTestCase(BaseSocialViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super(BaseSocialSubmissionViewTestCase, cls).setUpTestData()
        cls.submission = Submission(
            owner=cls.foo,
            title="Submission",
            description_raw="Description",
            content_raw="Content",
            ctime=timezone.now())
        cls.submission.save(update_content=True)
        cls.comment = Comment(
            owner=cls.bar,
            target_object_owner=cls.foo,
            object_model=cls.submission,
            body_raw="Comment")
        cls.comment.save()


class TestFavoriteSubmissionView(BaseSocialSubmissionViewTestCase):
    def test_submission_favorited(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:favorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'Submission favorited!')
        notification = Notification.objects.get(pk=1)
        self.assertEqual(notification.notification_type,
                         Notification.FAVORITE)

    def test_cant_favorite_own_submission(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'social:favorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'You cannot favorite your own '
                            'submission')

    def test_cant_favorite_submission_if_blocked(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.foo.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:favorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'You cannot favorite this submission, '
                            'as you have been blocked by the author.',
                            status_code=403)

    def test_cant_favorite_submission_if_already_favorited(self):
        self.bar.profile.favorited_submissions.add(self.submission)
        self.bar.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:favorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'You have already favorited this '
                            'submission')


class TestUnfavoriteSubmissionView(BaseSocialSubmissionViewTestCase):
    def test_submission_unfavorited(self):
        self.bar.profile.favorited_submissions.add(self.submission)
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.FAVORITE,
            subject=self.submission,
        ).save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:unfavorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'Submission removed from favorites.')
        self.assertEquals(self.foo.notification_set.count(), 0)

    def test_cant_unfavorite_own_submission(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'social:unfavorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'You cannot unfavorite your own '
                            'submission')

    def test_cant_unfavorite_submission_if_blocked(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.foo.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:unfavorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'You cannot unfavorite this submission, '
                            'as you have been blocked by the author.',
                            status_code=403)

    def test_cant_unfavorite_submission_if_already_unfavorited(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:unfavorite_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, "You haven't yet favorited this "
                            'submission')


class TestRateSubmissionView(BaseSocialSubmissionViewTestCase):
    def test_submission_rated(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:rate_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission'
            }), {'rating': 3}, follow=True)
        self.assertContains(response, 'Submission successfully rated.')
        notification = Notification.objects.get(pk=1)
        self.assertEqual(notification.notification_type, Notification.RATING)

    def test_submission_rerated(self):
        rating = Rating(
            owner=self.bar,
            submission=self.submission,
            rating=5)
        rating.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:rate_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission'
            }), {'rating': 3}, follow=True)
        rating.refresh_from_db()
        self.assertContains(response, 'Existing rating updated.')
        self.assertEqual(rating.rating, 3)
        notification = Notification.objects.get(pk=1)
        self.assertEqual(notification.notification_type, Notification.RATING)

    def test_invalid_rating(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:rate_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission'
            }), {'rating': 'asdf'}, follow=True)
        self.assertContains(response, 'Invalid rating specified.')
        response = self.client.post(reverse(
            'social:rate_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission'
            }), {'rating': -42}, follow=True)
        self.assertContains(response, 'Invalid rating specified.')

    def test_cant_rate_own_submission(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'social:rate_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission'
            }), {'rating': 5}, follow=True)
        self.assertContains(response, 'You cannot rate your own submission.')

    def test_cant_rate_submission_if_blocked(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.foo.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:rate_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission'
            }), {'rating': 3}, follow=True)
        self.assertContains(response, 'You cannot rate this submission, as '
                            'you have been blocked by the author.',
                            status_code=403)


class TestEnjoySubmissionView(BaseSocialSubmissionViewTestCase):
    def test_submission_enjoyed(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:enjoy_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'Enjoy vote added to submission!')
        notification = Notification.objects.get(pk=1)
        self.assertEqual(notification.notification_type, Notification.ENJOY)

    def test_cant_enjoy_submission_if_disallowed(self):
        self.submission.can_enjoy = False
        self.submission.save(update_content=True)
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:enjoy_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'The author has disabled enjoy voting '
                            'on this submission.')

    def test_cant_enjoy_own_submission(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'social:enjoy_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'You cannot add enjoy votes to your '
                            'own submission.')

    def test_cant_enjoy_submissions_if_blocked(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.foo.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse(
            'social:enjoy_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission',
            }), follow=True)
        self.assertContains(response, 'You cannot add enjoy votes to this '
                            'submission, as you have been blocked by the '
                            'author.', status_code=403)


class TestPostCommentView(BaseSocialSubmissionViewTestCase):
    def test_form_renders_if_logged_in(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(self.submission.get_absolute_url())
        self.assertContains(
            response,
            '<input type="hidden" name="parent" value="{}" />'.format(
                self.comment.id))
        self.assertContains(
            response,
            '<input id="id_object_id" name="object_id" type="hidden" '
            'value="{}" />'.format(self.submission.id),
            2)

    def test_form_not_present_if_logged_out(self):
        response = self.client.get(self.submission.get_absolute_url())
        self.assertNotContains(
            response,
            'Post reply')
        self.assertNotContains(
            response,
            'Add comment')

    def test_respects_can_comment_flag(self):
        self.submission.can_comment = False
        self.submission.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(self.submission.get_absolute_url())
        self.assertNotContains(
            response,
            'Post reply')
        self.assertNotContains(
            response,
            'Add comment')

    def test_post_comment(self):
        self.client.login(username='bar',
                          password='another good password')
        ctype = ContentType.objects.get(app_label='submissions',
                                        model='submission')
        response = self.client.post(reverse('social:post_comment'),
                                    {
                                        'content_type': ctype.id,
                                        'object_id': self.submission.id,
                                        'body_raw': 'A Second Comment',
                                    }, follow=True)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertContains(response, 'A Second Comment')

    def test_nest_comment(self):
        self.client.login(username='bar',
                          password='another good password')
        ctype = ContentType.objects.get(app_label='submissions',
                                        model='submission')
        response = self.client.post(reverse('social:post_comment'),
                                    {
                                        'content_type': ctype.id,
                                        'object_id': self.submission.id,
                                        'body_raw': 'A Second Comment',
                                        'parent': self.comment.id,
                                    }, follow=True)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertContains(response, 'A Second Comment')
        self.assertContains(response, '<div class="comment-reply">')

    def test_notifications(self):
        baz = User.objects.create_user('baz', 'baz@example.com',
                                       'another good password')
        baz.profile = Profile(profile_raw='Bazzo', display_name='Bad Wolf')
        baz.profile.save()
        self.client.login(username='baz',
                          password='another good password')
        ctype = ContentType.objects.get(app_label='submissions',
                                        model='submission')
        self.client.post(reverse('social:post_comment'),
                         {
                             'content_type': ctype.id,
                             'object_id': self.submission.id,
                             'body_raw': 'A Second Comment',
                             'parent': self.comment.id,
                         }, follow=True)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(
            [x.notification_type for x in Notification.objects.all()],
            [
                Notification.COMMENT_REPLY,
                Notification.SUBMISSION_COMMENT,
            ])

    def test_fail(self):
        self.submission.can_comment = False
        self.submission.save()
        self.client.login(username='bar',
                          password='another good password')
        ctype = ContentType.objects.get(app_label='submissions',
                                        model='submission')
        response = self.client.post(reverse('social:post_comment'),
                                    {
                                        'content_type': ctype.id,
                                        'object_id': self.submission.id,
                                        'body_raw': 'A Second Comment',
                                    }, follow=True)
        self.assertContains(response, 'There was an error posting that '
                            'comment')


class TestDeleteCommentView(BaseSocialSubmissionViewTestCase):
    def test_renders_form_if_applicable(self):
        # Logged out users do not see
        response = self.client.get(self.submission.get_absolute_url())
        self.assertNotContains(
            response,
            'Delete comment')
        # Unrelated users do not see
        baz = User.objects.create_user('baz', 'baz@example.com',
                                       'another good password')
        baz.profile = Profile(profile_raw='Bazzo', display_name='Bad Wolf')
        baz.profile.save()
        self.client.login(username='baz',
                          password='another good password')
        response = self.client.get(self.submission.get_absolute_url())
        self.assertNotContains(
            response,
            'Delete comment')
        # Comment owner sees
        self.client.logout()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(self.submission.get_absolute_url())
        self.assertContains(
            response,
            'Delete comment')
        # Page owner sees
        self.client.logout()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(self.submission.get_absolute_url())
        self.assertContains(
            response,
            'Delete comment')

    def test_renders_deleted_comment(self):
        self.comment.deleted = True
        self.comment.save()
        response = self.client.get(self.submission.get_absolute_url())
        self.assertContains(
            response,
            'This comment has been deleted by the commenter.')
        self.comment.deleted_by_object_owner = True
        self.comment.save()
        response = self.client.get(self.submission.get_absolute_url())
        self.assertContains(
            response,
            'This comment has been deleted by the page owner.')

    def test_comment_owner_delete(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.post(reverse('social:delete_comment'),
                                    {
                                        'comment_id': self.comment.id,
                                    }, follow=True)
        self.assertContains(
            response,
            'This comment has been deleted by the commenter.')

    def test_target_owner_delete(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('social:delete_comment'),
                                    {
                                        'comment_id': self.comment.id,
                                    }, follow=True)
        self.assertContains(
            response,
            'This comment has been deleted by the page owner.')

    def test_notifications_wiped(self):
        baz = User.objects.create_user('baz', 'baz@example.com',
                                       'another good password')
        baz.profile = Profile(profile_raw='Bazzo', display_name='Bad Wolf')
        baz.profile.save()
        self.client.login(username='baz',
                          password='another good password')
        ctype = ContentType.objects.get(app_label='submissions',
                                        model='submission')
        self.client.post(reverse('social:post_comment'),
                         {
                             'content_type': ctype.id,
                             'object_id': self.submission.id,
                             'body_raw': 'A Second Comment',
                             'parent': self.comment.id,
                         }, follow=True)
        self.assertEqual(Notification.objects.count(), 2)
        self.client.post(reverse('social:delete_comment'),
                         {
                             'comment_id': 2,
                         }, follow=True)
        self.assertEqual(Notification.objects.count(), 0)

    def test_forbidden(self):
        baz = User.objects.create_user('baz', 'baz@example.com',
                                       'another good password')
        baz.profile = Profile(profile_raw='Bazzo', display_name='Bad Wolf')
        baz.profile.save()
        self.client.login(username='baz',
                          password='another good password')
        response = self.client.post(reverse('social:delete_comment'),
                                    {
                                        'comment_id': self.comment.id,
                                    }, follow=True)
        self.assertContains(
            response,
            'You may only delete a comment if you are the poster or the page '
            'owner')


class TestNotificationBadges(BaseSocialSubmissionViewTestCase):
    def test_empty_badges(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('core:front'))
        self.assertContains(response, '<span class="badge"></span>', count=5)

    def test_badges(self):
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.WATCH,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            subject=self.submission,
            notification_type=Notification.FAVORITE,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.MESSAGE,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.APPLICATION_CLAIMED).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('core:front'))
        self.assertContains(response, '<span class="badge">4</span>')
        self.assertContains(response, '<span class="badge">1</span>', count=4)


class TestViewNotificationsCategoriesView(BaseSocialSubmissionViewTestCase):
    def test_no_notifications(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_categories'))
        self.assertContains(response, '<h2>No notifications <small>Lucky '
                            'you!</small></h2>')

    def test_notifications(self):
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.WATCH,
        ).save()
        rating = Rating(owner=self.bar, submission=self.submission, rating=3)
        rating.save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.RATING,
            subject=rating,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.ENJOY,
            subject=self.submission,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            subject=self.submission,
            notification_type=Notification.FAVORITE,
        ).save()
        comment = Comment(
            owner=self.bar,
            object_model=self.submission,
            target_object_owner=self.foo,
            body_raw='asdf'
        )
        comment.save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.SUBMISSION_COMMENT,
            subject=comment,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.COMMENT_REPLY,
            subject=comment,
        ).save()
        Notification(
            target=self.foo,
            notification_type=Notification.PROMOTE,
            subject=self.submission,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.HIGHLIGHT,
            subject=self.submission,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.MESSAGE,
        ).save()
        app = Application(
            applicant=self.foo,
            application_type=Application.AD).save()
        Notification(
            target=self.foo,
            source=self.bar,
            subject=app,
            notification_type=Notification.APPLICATION_CLAIMED).save()
        Notification(
            target=self.foo,
            source=self.bar,
            subject=app,
            notification_type=Notification.APPLICATION_RESOLVED).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_categories'))
        self.assertContains(response, '>Administration notifications</h2>')
        self.assertContains(response, '<h3>Application resolutions</h3>')
        self.assertContains(response, '<h3>Application claims</h3>')
        self.assertContains(response, '>Messages</h2>')
        self.assertContains(response, '>User Notifications</h2>')
        self.assertContains(response, '>Submission Notifications</h2>')
        self.assertContains(response, '<h3>Favorites</h3>')
        self.assertContains(response, '<h3>Ratings</h3>')
        self.assertContains(response, '<h3>Enjoy votes</h3>')
        self.assertContains(response, '<h3>Submission comments</h3>')
        self.assertContains(response, '<h3>Comment replies</h3>')
        self.assertContains(response, '<h3>Promotions</h3>')
        self.assertContains(response, '<h3>Highlights</h3>')
        self.assertContains(response, '<input type="checkbox" '
                            'name="notification_id"', count=11)

    def test_expired_notifications(self):
        self.foo.profile.expired_notifications = 5
        self.foo.profile.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_categories'))
        self.assertContains(response, 'You have 5 notifications that have '
                            'expired.')


class TestViewNotificationsTimelineView(BaseSocialSubmissionViewTestCase):
    def test_no_notifications(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_timeline'))
        self.assertContains(response, '<h2>No notifications <small>Lucky '
                            'you!</small></h2>')

    def test_notifications(self):
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.WATCH,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            subject=self.submission,
            notification_type=Notification.FAVORITE,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.MESSAGE,
        ).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_timeline'))
        self.assertContains(response, '"list-group-item striped-item"',
                            count=3)

    def test_notifications_paginate(self):
        for i in range(1, 100):
            Notification(
                target=self.foo,
                source=self.bar,
                subject=self.submission,
                notification_type=Notification.ENJOY,
            ).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_timeline'))
        self.assertContains(response, '>(current)<')
        self.assertContains(response, '2</a>')
        response = self.client.get(reverse(
            'social:view_notifications_timeline', kwargs={
                'page': 50,
            }))
        self.assertContains(response, '>(current)<')
        self.assertContains(response, '1</a>')


class TestRemoveNotificationsView(BaseSocialViewTestCase):
    def test_removes_notifications(self):
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.WATCH,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.WATCH,
        ).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('social:remove_notifications'),
                                    {'notification_id': [1, 2]},
                                    follow=True)
        self.assertContains(response, 'Notifications deleted.')
        self.assertContains(response, '<h2>No notifications <small>Lucky '
                            'you!</small></h2>')

    def test_ignores_missing_notifications(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('social:remove_notifications'),
                                    {'notification_id': 42},
                                    follow=True)
        self.assertContains(response, 'Notifications deleted.')
        self.assertContains(response, '<h2>No notifications <small>Lucky '
                            'you!</small></h2>')

    def test_warns_and_stops_on_not_own_notification(self):
        Notification(
            target=self.bar,
            source=self.foo,
            notification_type=Notification.WATCH,
        ).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('social:remove_notifications'),
                                    {'notification_id': 1},
                                    follow=True)
        self.assertContains(response, 'Permission denied', status_code=403)


class TestNukeNotificationsView(BaseSocialSubmissionViewTestCase):
    def test_nukes_notifications(self):
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.WATCH,
        ).save()
        rating = Rating(owner=self.bar, submission=self.submission, rating=3)
        rating.save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.RATING,
            subject=rating,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.ENJOY,
            subject=self.submission,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            subject=self.submission,
            notification_type=Notification.FAVORITE,
        ).save()
        comment = Comment(
            owner=self.bar,
            object_model=self.submission,
            target_object_owner=self.foo,
            body_raw='asdf'
        )
        comment.save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.SUBMISSION_COMMENT,
            subject=comment,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.COMMENT_REPLY,
            subject=comment,
        ).save()
        Notification(
            target=self.foo,
            notification_type=Notification.PROMOTE,
            subject=self.submission,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.HIGHLIGHT,
            subject=self.submission,
        ).save()
        Notification(
            target=self.foo,
            source=self.bar,
            notification_type=Notification.MESSAGE,
        ).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('social:nuke_notifications'),
                                    follow=True)
        self.assertContains(response, 'All notifications nuked.')
        self.assertContains(response, '<h2>No notifications <small>Lucky '
                            'you!</small></h2>')

    def test_clears_expired_notifivations(self):
        self.foo.profile.expired_notifications = 5
        self.foo.profile.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('social:nuke_notifications'),
                                    follow=True)
        self.assertContains(response, 'All notifications nuked.')
        self.assertContains(response, '<h2>No notifications <small>Lucky '
                            'you!</small></h2>')
