import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Activity
from usermgmt.models import Profile


class ActivityBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.foo = User.objects.create_user('foo', 'foo@example.com',
                                           'a good password')
        cls.foo.save()
        cls.foo.profile = Profile()
        cls.foo.profile.save()
        cls.bar = User.objects.create_user('bar', 'bar@example.com',
                                           'another good password')
        cls.bar.save()
        cls.bar.profile = Profile()
        cls.bar.profile.save()


class TestModels(ActivityBaseTestCase):
    def test_create(self):
        self.assertEqual(Activity.objects.count(), 2)
        activity = Activity.create('user', 'login', self.foo)
        self.assertEqual(activity.activity_type, 'user:login')
        self.assertEqual(Activity.objects.count(), 3)

    def test_ignores_unknown_type(self):
        self.assertEqual(Activity.objects.count(), 2)
        activity = Activity.create('bad', 'wolf', self.foo)
        self.assertEqual(activity, None)
        self.assertEqual(Activity.objects.count(), 2)


class TestGetStreamView(ActivityBaseTestCase):
    def generate_activity_items(self):
        self.client.login(username='foo',
                          password='a good password')
        self.client.logout()
        self.client.login(username='bar',
                          password='another good password')

    def test_full_stream(self):
        self.generate_activity_items()
        response = self.client.get(reverse('activitystream:get_stream'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 5)
        self.assertEqual([item['type'] for item in data], [
            'user:login',
            'user:logout',
            'user:login',
            'user:reg',
            'user:reg',
        ])

    def test_limit_to_content_type(self):
        self.generate_activity_items()
        response = self.client.get(reverse(
            'activitystream:get_stream', kwargs={
                'models': 'auth:user',
            }))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 5)
        self.assertEqual([item['type'] for item in data], [
            'user:login',
            'user:logout',
            'user:login',
            'user:reg',
            'user:reg',
        ])

    def test_limit_to_object(self):
        self.generate_activity_items()
        response = self.client.get(reverse(
            'activitystream:get_stream', kwargs={
                'models': 'auth:user',
                'object_id': self.foo.id,
            }))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)
        self.assertEqual([item['type'] for item in data], [
            'user:logout',
            'user:login',
            'user:reg',
        ])

    def test_limit_to_activity_type(self):
        self.generate_activity_items()
        response = self.client.get(reverse('activitystream:get_stream'), {
            'type': 'user:reg',
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 2)
        self.assertEqual([item['type'] for item in data], [
            'user:reg',
            'user:reg',
        ])


class TestSitewideDataView(ActivityBaseTestCase):
    def test_results(self):
        self.maxDiff = None
        response = self.client.get(reverse('activitystream:sitewide_data'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data['version']['full']), 40)
        data['version']['full'] = 'revno'
        self.assertEqual(len(data['version']['short']), 7)
        data['version']['short'] = 'revno'
        self.assertEqual(data, {
            u'adminflags': 0,
            u'ads': {u'live': 0, u'total': 0},
            u'comments': 0,
            u'enjoys': 0,
            u'favorites': 0,
            u'folders': 0,
            u'friendgroups': 0,
            u'groups': {},
            u'promotions': {u'all_active': 0,
                            u'highlight': 0,
                            u'paid_promotions': 0,
                            u'promotions': 0},
            u'publishers': 0,
            u'ratings': {u'1star': 0,
                         u'2star': 0,
                         u'3star': 0,
                         u'4star': 0,
                         u'5star': 0,
                         u'total': 0},
            u'submissions': 0,
            u'tags': {u'taggeditems': 0, u'tags': 0},
            u'users': {u'all': 2, u'staff': 0, u'superusers': 0},
            u'version': {u'full': u'revno',
                         u'short': u'revno',
                         u'version': u'pre-release'}
        })
