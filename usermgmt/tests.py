from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Profile


class RegisterViewTests(TestCase):
    def test_form_renders(self):
        response = self.client.get(reverse('usermgmt:register'))
        self.assertEqual(response.context['title'], 'Register')
        self.assertContains(response, 'Username')

    def test_successful_registration(self):
        response = self.client.post(
            reverse('usermgmt:register'),
            {
                'username': 'foo',
                'email': 'bar@example.com',
                'password1': 'asdfqwer',
                'password2': 'asdfqwer',
            },
            follow=True)
        self.assertContains(response, '~foo')

    def test_register_while_login_disallowed(self):
        foo = User(username='foo')
        foo.save()
        self.client.force_login(foo)
        response = self.client.get(reverse('usermgmt:register'))
        self.assertContains(response, "Whoops!  You're already registered and "
                            "logged in!")

    def test_duplicate_username_disallowed(self):
        foo = User(username='foo')
        foo.save()
        response = self.client.post(
            reverse('usermgmt:register'),
            {
                'username': 'foo',
                'email': 'bar@example.com',
                'password1': 'asdfqwer',
                'password2': 'asdfqwer',
            },
            follow=True)
        self.assertContains(response, 'A user with that username already '
                            'exists.')


class UpdateProfileViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.foo = User.objects.create_user('foo', 'foo@example.com',
                                           'a good password')
        cls.foo.profile = Profile(profile_raw='Wow!',
                                  display_name='Mx Foo Bar')
        cls.foo.profile.save()

    def test_page_renders(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('usermgmt:update_profile'))
        self.assertContains(response, 'Mx Foo Bar')

    def test_data_saved_with_markdown(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.post(
            reverse('usermgmt:update_profile'),
            {
                'display_name': 'Mx Foo Bar-Baz',
                'profile_raw': '*wow*',
            },
            follow=True)
        user = response.context['user']
        self.assertEqual(user.profile.display_name, 'Mx Foo Bar-Baz')
        self.assertEqual(user.profile.profile_rendered, '<p><em>wow</em></p>')


class ViewProfileTests(TestCase):
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

    def test_page_renders(self):
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('foo',)))
        self.assertContains(response, 'Wow!')

    def test_page_has_social_if_logged_in_and_other_user(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('bar',)))
        # TODO make this check more robust
        self.assertContains(response, 'Social')

    def test_page_doesnt_have_social_if_same_user(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('foo',)))
        # TODO make this check more robust
        self.assertNotContains(response, 'Social')

    def test_page_doesnt_have_social_if_not_logged_in(self):
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('foo',)))
        # TODO make this check more robust
        self.assertNotContains(response, 'Social')

    def test_page_has_block_if_unblocked(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('bar',)))
        self.assertContains(response, '>Block user<')

    def test_page_has_unblock_if_blocked(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('bar',)))
        self.assertContains(response, '>Unblock user<')

    def test_page_has_watch_if_unwatched(self):
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('bar',)))
        self.assertContains(response, '>Follow user<')

    def test_page_has_unwatch_if_watched(self):
        self.foo.profile.watched_users.add(self.bar)
        self.client.login(username='foo', password='a good password')
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('bar',)))
        self.assertContains(response, '>Unfollow user<')

    def test_page_shows_when_blocked(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.client.login(username='bar', password='another good password')
        response = self.client.get(reverse('usermgmt:view_profile',
                                           args=('foo',)))
        self.assertContains(response, 'You are blocked from viewing this '
                            'profile by the owner')
