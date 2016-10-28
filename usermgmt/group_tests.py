from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Profile
from .group_models import FriendGroup


class BaseGroupViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.foo = User.objects.create_user('foo', 'foo@example.com',
                                           'a good password')
        cls.foo.profile = Profile(profile_raw='Wow!',
                                  display_name='Mx Foo Bar')
        cls.foo.profile.save()
        cls.bar = User.objects.create_user('bar', 'bar@example.com',
                                           'another good password')
        cls.bar.profile = Profile(profile_raw='Whoa', display_name='Bad Wolf',
                                  results_per_page=1)
        cls.bar.profile.save()
        cls.foo.profile.watched_users.add(cls.bar)
        cls.group = FriendGroup(name='Group 1')
        cls.group.save()
        cls.foo.profile.friend_groups.add(cls.group)


class TestListGroupsView(BaseGroupViewsTestCase):
    def test_renders_no_groups(self):
        self.client.login(username='foo',
                          password='a good password')
        self.group.delete()
        response = self.client.get(reverse(
            'usermgmt:list_groups', kwargs={
                'username': 'foo',
            }))
        self.assertNotContains(response, 'Group 1</a>')

    def test_lists_groups(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'usermgmt:list_groups', kwargs={
                'username': 'foo',
            }))
        self.assertContains(response, 'Group 1</a>')


class TestCreateGroupView(BaseGroupViewsTestCase):
    def test_form_renders(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'usermgmt:create_group', kwargs={
                'username': 'foo',
            }))
        self.assertContains(response, 'Create a new group')
        self.assertContains(response, 'value="Save group"')

    def test_can_save_form_no_members(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'usermgmt:create_group', kwargs={
                'username': 'foo',
            }), {
                'name': 'Group 2',
                'members': [],
            }, follow=True)
        self.assertContains(response, 'Group 2')

    def test_can_save_form_members(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'usermgmt:create_group', kwargs={
                'username': 'foo',
            }), {
                'name': 'Group 2',
                'members': [self.bar.id],
            }, follow=True)
        self.assertContains(response, 'Group 2')
        self.assertContains(response, 'Bad Wolf')


class TestViewGroupView(BaseGroupViewsTestCase):
    def test_renders_empty_group(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'usermgmt:view_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }))
        self.assertNotContains(response, 'Bad Wolf')
        self.assertNotContains(response, 'group-member')

    def test_lists_group_members(self):
        self.client.login(username='foo',
                          password='a good password')
        self.group.users.add(self.bar)
        response = self.client.get(reverse(
            'usermgmt:view_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }))
        self.assertContains(response, 'Bad Wolf')
        self.assertContains(response, 'group-member', 1)

    def test_other_users_group_forbidden(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'usermgmt:view_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }))
        self.assertEqual(response.status_code, 403)


class TestEditGroupView(BaseGroupViewsTestCase):
    def test_form_renders(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'usermgmt:edit_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }))
        self.assertContains(response, 'Edit group "Group 1"')
        self.assertContains(response, 'value="Save group"')

    def test_can_save_form_no_members(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'usermgmt:edit_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }), {
                'name': 'Group 2',
                'members': [],
            }, follow=True)
        self.assertContains(response, 'Group 2')

    def test_can_save_form_members(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'usermgmt:edit_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }), {
                'name': 'Group 2',
                'members': [self.bar.id],
            }, follow=True)
        self.assertContains(response, 'Group 2')
        self.assertContains(response, 'Bad Wolf')

    def test_can_save_form_remove_members(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'usermgmt:edit_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }), {
                'name': 'Group 2',
                'members': [],
            }, follow=True)
        self.assertContains(response, 'Group 2')
        self.assertNotContains(response, 'Bad Wolf')

    def test_other_users_group_forbidden(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'usermgmt:edit_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }))
        self.assertEqual(response.status_code, 403)


class TestDeleteGroupView(BaseGroupViewsTestCase):
    def test_ask_for_confirmation(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'usermgmt:delete_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }))
        self.assertContains(response, 'You are about to delete your group '
                            'Group 1.')

    def test_delete_on_confirmation(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'usermgmt:delete_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }), {}, follow=True)
        self.assertContains(response, 'Group deleted.')

    def test_other_users_group_forbidden(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'usermgmt:delete_group', kwargs={
                'username': 'foo',
                'group_id': self.group.id,
            }))
        self.assertEqual(response.status_code, 403)
