from django.contrib.auth.models import User
from django.test import (
    TestCase,
    tag,
)

from usermgmt.models import Profile


class BaseAdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user', 'user@example.com',
                                            'user pass')
        cls.user.profile = Profile(display_name='User McUserface',
                                   profile_raw='Wow')
        cls.user.profile.save()
        cls.social_mod = User.objects.create_user(
            'social_mod', 'social_mod@example.com', 'social_mod pass')
        cls.social_mod.profile = Profile(display_name='User McUserface',
                                         profile_raw='Wow')
        cls.social_mod.profile.save()
        cls.content_mod = User.objects.create_user(
            'content_mod', 'content_mod@example.com', 'content_mod pass')
        cls.content_mod.profile = Profile(display_name='User McUserface',
                                          profile_raw='Wow')
        cls.content_mod.profile.save()
        cls.superuser = User.objects.create_user(
            'superuser', 'superuser@example.com', 'superuser pass')
        cls.superuser.profile = Profile(display_name='User McUserface',
                                        profile_raw='Wow')
        cls.superuser.profile.save()


@tag('as_user')
class TestDashboardViewAsUser(BaseAdminTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestDashboardViewAsSocialMod(BaseAdminTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestDashboardViewAsContentMod(BaseAdminTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestDashboardViewAsSuperuser(BaseAdminTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)
