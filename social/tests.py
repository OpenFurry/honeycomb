from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from usermgmt.models import Profile


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
        response = self.client.get(reverse('social:watch_user', args=('bar',)),
                                   follow=True)
        self.assertContains(response, "You are now watching bar!")
        self.assertIn(self.bar, self.foo.profile.watched_users.all())

    def test_cant_watch_self(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:watch_user', args=('foo',)),
                                   follow=True)
        self.assertContains(response, "watch yourself.")

    def test_already_watched(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.watched_users.add(self.bar)
        response = self.client.get(reverse('social:watch_user', args=('bar',)),
                                   follow=True)
        self.assertContains(response, 'You are already watching this user.')

    def test_404(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:watch_user',
                                   args=('bad-wolf',)),
                                   follow=True)
        self.assertEqual(response.status_code, 404)


class TestUnwatchUserView(BaseSocialViewTestCase):
    def test_user_unwatched(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.watched_users.add(self.bar)
        response = self.client.get(reverse('social:unwatch_user',
                                   args=('bar',)),
                                   follow=True)
        self.assertContains(response, "You are no longer watching bar.")
        self.assertNotIn(self.bar, self.foo.profile.watched_users.all())

    def test_cant_unwatch_self(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:unwatch_user',
                                   args=('foo',)),
                                   follow=True)
        self.assertContains(response, "unwatch yourself.")

    def test_not_watching(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:unwatch_user',
                                   args=('bar',)),
                                   follow=True)
        self.assertContains(response, 'You are not watching this user.')

    def test_404(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:unwatch_user',
                                   args=('bad-wolf',)),
                                   follow=True)
        self.assertEqual(response.status_code, 404)


class TestBlockUserView(BaseSocialViewTestCase):
    def test_user_blocked(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:block_user', args=('bar',)),
                                   follow=True)
        self.assertContains(response, 'You are now blocking bar from viewing '
                            'your profile and submissions!')
        self.assertIn(self.bar, self.foo.profile.blocked_users.all())

    def test_cant_block_self(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:block_user', args=('foo',)),
                                   follow=True)
        self.assertContains(response, "block yourself.")

    def test_already_blocked(self):
        self.client.login(username='foo', password='a good password')
        self.foo.profile.blocked_users.add(self.bar)
        response = self.client.get(reverse('social:block_user', args=('bar',)),
                                   follow=True)
        self.assertContains(response, 'You are already blocking this user.')

    def test_404(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('social:block_user',
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
