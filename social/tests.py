from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import (
    Comment,
    Rating,
)
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
        cls.submission = Submission(
            owner=cls.foo,
            title="Submission",
            description_raw="Description",
            content_raw="Content")
        cls.submission.save()


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


class TestFavoriteSubmissionView(BaseSocialViewTestCase):
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


class TestUnfavoriteSubmissionView(BaseSocialViewTestCase):
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


class TestRateSubmissionView(BaseSocialViewTestCase):
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


class TestEnjoySubmissionView(BaseSocialViewTestCase):
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
        self.submission.save()
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


class TestNotificationBadges(BaseSocialViewTestCase):
    def test_empty_badges(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('core:front'))
        self.assertContains(response, '<span class="badge"></span>', count=4)

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
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('core:front'))
        self.assertContains(response, '<span class="badge">3</span>')
        self.assertContains(response, '<span class="badge">1</span>', count=3)


class TestViewNotificationsCategoriesView(BaseSocialViewTestCase):
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
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_categories'))
        self.assertContains(response, '<h2>Messages</h2>')
        self.assertContains(response, '<h2>User Notifications</h2>')
        self.assertContains(response, '<h2>Submission Notifications</h2>')
        self.assertContains(response, '<h3>Favorites</h3>')
        self.assertContains(response, '<h3>Ratings</h3>')
        self.assertContains(response, '<h3>Enjoy votes</h3>')
        self.assertContains(response, '<h3>Submission comments</h3>')
        self.assertContains(response, '<h3>Comment replies</h3>')
        self.assertContains(response, '<h3>Promotions</h3>')
        self.assertContains(response, '<h3>Highlights</h3>')
        self.assertContains(response, '<input type="checkbox" '
                            'name="notification_id"', count=9)

    def test_expired_notifications(self):
        self.foo.profile.expired_notifications = 5
        self.foo.profile.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'social:view_notifications_categories'))
        self.assertContains(response, 'You have 5 notifications that have '
                            'expired.')


class TestViewNotificationsTimelineView(BaseSocialViewTestCase):
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


class TestNukeNotificationsView(BaseSocialViewTestCase):
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