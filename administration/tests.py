from django.contrib.auth.models import (
    Group,
    User,
)
from django.core.urlresolvers import reverse
from django.test import (
    TestCase,
    tag,
)

from .models import Application
from usermgmt.models import Profile


class BaseAdminTestCase(TestCase):
    fixtures = ['groups.json']

    @classmethod
    def setUpTestData(cls):
        social_moderators = Group.objects.get(name='Social moderators')
        content_moderators = Group.objects.get(name='Content moderators')
        cls.user = User.objects.create_user('user', 'user@example.com',
                                            'user pass')
        cls.user.profile = Profile(display_name='User McUserface',
                                   profile_raw='Wow')
        cls.user.profile.save()
        cls.social_mod = User.objects.create_user(
            'social_mod', 'social_mod@example.com', 'social_mod pass')
        cls.social_mod.profile = Profile(display_name='Social Modface',
                                         profile_raw='Wow')
        cls.social_mod.profile.save()
        cls.social_mod.groups.add(social_moderators)
        cls.social_mod.is_staff = True
        cls.social_mod.save()
        cls.content_mod = User.objects.create_user(
            'content_mod', 'content_mod@example.com', 'content_mod pass')
        cls.content_mod.profile = Profile(display_name='Content Modface',
                                          profile_raw='Wow')
        cls.content_mod.profile.save()
        cls.content_mod.groups.add(content_moderators)
        cls.content_mod.is_staff = True
        cls.content_mod.save()
        cls.superuser = User.objects.create_user(
            'superuser', 'superuser@example.com', 'superuser pass')
        cls.superuser.profile = Profile(display_name='Super Q. User',
                                        profile_raw='Wow')
        cls.superuser.profile.save()
        cls.superuser.is_staff = True
        cls.superuser.is_superuser = True
        cls.superuser.save()


@tag('as_user')
class TestDashboardViewAsUser(BaseAdminTestCase):

    def test_renders_no_applications(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_doesnt_render_others_applications(self):
        Application(
            applicant=self.social_mod,
            application_type=Application.AD).save()
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_doesnt_render_resolved_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.AD,
            resolution=Application.ACCEPTED).save()
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_renders_own_unresolved_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'Create an ad')


@tag('as_social_mod')
class TestDashboardViewAsSocialMod(BaseAdminTestCase):

    def test_renders_no_applications(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_doesnt_render_others_content_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_doesnt_render_resolved_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER,
            resolution=Application.ACCEPTED).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_renders_social_unresolved_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'Claim a publisher')

    def test_renders_own_unresolved_applications(self):
        Application(
            applicant=self.social_mod,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'Create an ad')


@tag('as_content_mod')
class TestDashboardViewAsContentMod(BaseAdminTestCase):

    def test_renders_no_applications(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_doesnt_render_others_social_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_doesnt_render_resolved_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.AD,
            resolution=Application.ACCEPTED).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_renders_content_unresolved_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'Create an ad')

    def test_renders_own_unresolved_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'Claim a publisher')


@tag('as_superuser')
class TestDashboardViewAsSuperuser(BaseAdminTestCase):

    def test_renders_no_applications(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_doesnt_render_resolved_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.AD,
            resolution=Application.ACCEPTED).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'No applications to display')

    def test_renders_all_unresolved_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:dashboard'))
        self.assertContains(response, 'Create an ad')
        self.assertContains(response, 'Claim a publisher')
