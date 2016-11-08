from django.core.urlresolvers import reverse
from django.test import tag

from .models import Application
from .tests import BaseAdminTestCase


@tag('as_user')
class TestListAllApplicationsViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_all_applications'))
        self.assertTrue(response.status_code, 403)


@tag('as_social_mod')
class TestListAllApplicationsViewAsSocialMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:list_all_applications'))
        self.assertTrue(response.status_code, 403)


@tag('as_content_mod')
class TestListAllApplicationsViewAsContentMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:list_all_applications'))
        self.assertTrue(response.status_code, 403)


@tag('as_superuser')
class TestListAllApplicationsViewAsSuperuser(BaseAdminTestCase):
    def test_renders_no_applications(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_all_applications'))
        self.assertContains(response, 'No applications to display')

    def test_renders_all_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_all_applications'))
        self.assertContains(response, 'Create an ad')
        self.assertContains(response, 'Claim a publisher')


@tag('as_user')
class TestListSocialApplicationsViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertTrue(response.status_code, 403)


@tag('as_social_mod')
class TestListSocialApplicationsViewAsSocialMod(BaseAdminTestCase):
    def test_renders_no_applications(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertContains(response, 'No applications to display')

    def test_renders_social_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertContains(response, 'Claim a publisher')


@tag('as_content_mod')
class TestListSocialApplicationsViewAsContentMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertTrue(response.status_code, 403)


@tag('as_superuser')
class TestListSocialApplicationsViewAsSuperuser(BaseAdminTestCase):
    def test_renders_no_applications(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertContains(response, 'No applications to display')

    def test_renders_social_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertContains(response, 'Claim a publisher')


@tag('as_user')
class TestListContentApplicationsViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_content_applications'))
        self.assertTrue(response.status_code, 403)


@tag('as_social_mod')
class TestListContentApplicationsViewAsSocialMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:list_content_applications'))
        self.assertTrue(response.status_code, 403)


@tag('as_content_mod')
class TestListContentApplicationsViewAsContentMod(BaseAdminTestCase):
    def test_renders_no_applications(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:list_content_applications'))
        self.assertContains(response, 'No applications to display')

    def test_renders_content_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertContains(response, 'Claim a publisher')


@tag('as_superuser')
class TestListContentApplicationsViewAsSuperuser(BaseAdminTestCase):
    def test_renders_no_applications(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_content_applications'))
        self.assertContains(response, 'No applications to display')

    def test_renders_content_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_social_applications'))
        self.assertContains(response, 'Claim a publisher')


class TestCreateApplicationView(BaseAdminTestCase):
    def test_form_renders(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:create_application'))
        self.assertContains(response, 'I would like to...')

    def test_creates_application(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(reverse(
            'administration:create_application'), {
                'application_type': Application.AD,
                'body_raw': 'asdf',
            }, follow=True)
        self.assertContains(response, "User McUserface's application to "
                            "create an ad")
        self.assertEqual(self.user.applications.count(), 1)


@tag('as_user')
class TestViewApplicationViewAsUser(BaseAdminTestCase):
    def test_doesnt_render_others_application(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertEqual(response.status_code, 403)

    def test_renders_own_application(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertContains(response, 'Claim a publisher')


@tag('as_social_mod')
class TestViewApplicationViewAsSocialMod(BaseAdminTestCase):
    def test_renders_others_social_application(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertContains(response, 'Claim a publisher')

    def test_doesnt_render_others_content_application(self):
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertEqual(response.status_code, 403)

    def test_renders_own_application(self):
        Application(
            applicant=self.social_mod,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertContains(response, 'Create an ad')


@tag('as_content_mod')
class TestViewApplicationViewAsContentMod(BaseAdminTestCase):
    def test_renders_others_content_application(self):
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertContains(response, 'Create an ad')

    def test_doesnt_render_others_social_application(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertEqual(response.status_code, 403)

    def test_renders_own_application(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertContains(response, 'Claim a publisher')


@tag('as_superuser')
class TestViewApplicationViewAsSuperuser(BaseAdminTestCase):
    def test_renders_all_applications(self):
        Application(
            applicant=self.content_mod,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 1,
            }))
        self.assertContains(response, 'Claim a publisher')
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:view_application', kwargs={
                'application_id': 2,
            }))
        self.assertContains(response, 'Create an ad')


class TestListParticipatingApplicationsViewAsUser(BaseAdminTestCase):
    def test_renders_own_applications(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_participating_applications'))
        self.assertContains(response, 'No applications to display')

    def test_renders_admin_contact_applications(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_participating_applications'))
        self.assertContains(response, 'Create an ad')
        self.assertContains(response, 'Claim a publisher')


@tag('as_user')
class TestClaimApplicationViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(reverse(
            'administration:claim_application', kwargs={'application_id': 1}))
        self.assertTrue(response.status_code, 403)


@tag('as_social_mod')
class TestClaimApplicationViewAsSocialMod(BaseAdminTestCase):
    def test_can_claim_social_application(self):
        a1 = Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER)
        a1.save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:claim_application', kwargs={
                'application_id': 1,
            }), follow=True)
        self.assertContains(response, 'Application claimed.')
        a1.refresh_from_db()
        self.assertEqual(a1.admin_contact, self.social_mod)

    def test_cant_claim_content_application(self):
        Application(
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:claim_application', kwargs={
                'application_id': 1,
            }), follow=True)
        self.assertEqual(response.status_code, 403)


@tag('as_content_mod')
class TestClaimApplicationViewAsContentMod(BaseAdminTestCase):
    def test_can_claim_content_application(self):
        a1 = Application(
            applicant=self.user,
            application_type=Application.AD)
        a1.save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:claim_application', kwargs={
                'application_id': 1,
            }), follow=True)
        self.assertContains(response, 'Application claimed.')
        a1.refresh_from_db()
        self.assertEqual(a1.admin_contact, self.content_mod)

    def test_cant_claim_social_application(self):
        Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:claim_application', kwargs={
                'application_id': 1,
            }), follow=True)
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestClaimApplicationViewAsSuperuser(BaseAdminTestCase):
    def test_can_claim_all_applications(self):
        a1 = Application(
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER)
        a1.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:claim_application', kwargs={
                'application_id': 1,
            }), follow=True)
        self.assertContains(response, 'Application claimed.')
        a1.refresh_from_db()
        self.assertEqual(a1.admin_contact, self.superuser)
        a2 = Application(
            applicant=self.user,
            application_type=Application.AD)
        a2.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:claim_application', kwargs={
                'application_id': 2,
            }), follow=True)
        self.assertContains(response, 'Application claimed.')
        a2.refresh_from_db()
        self.assertEqual(a2.admin_contact, self.superuser)


@tag('as_user')
class TestResolveApplicationViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1
            }))
        self.assertTrue(response.status_code, 403)


@tag('as_social_mod')
class TestResolveApplicationViewAsSocialMod(BaseAdminTestCase):
    def test_can_resolve_social_application(self):
        a1 = Application(
            admin_contact=self.social_mod,
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER)
        a1.save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1,
            }), {'resolution': 'a'}, follow=True)
        self.assertContains(response, 'The application has been resolved.')
        a1.refresh_from_db()
        self.assertEqual(a1.resolution, 'a')

    def test_cant_resolve_content_application(self):
        Application(
            admin_contact=self.social_mod,
            applicant=self.user,
            application_type=Application.AD).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1,
            }), {'resolution': 'a'}, follow=True)
        self.assertEqual(response.status_code, 403)


@tag('as_content_mod')
class TestResolveApplicationViewAsContentMod(BaseAdminTestCase):
    def test_can_resolve_content_application(self):
        a1 = Application(
            admin_contact=self.content_mod,
            applicant=self.user,
            application_type=Application.AD)
        a1.save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1,
            }), {'resolution': 'a'}, follow=True)
        self.assertContains(response, 'The application has been resolved.')
        a1.refresh_from_db()
        self.assertEqual(a1.resolution, 'a')

    def test_cant_resolve_social_application(self):
        Application(
            admin_contact=self.content_mod,
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER).save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1,
            }), {'resolution': 'a'}, follow=True)
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestResolveApplicationViewAsSuperuser(BaseAdminTestCase):
    def test_invalid_resolution(self):
        a1 = Application(
            admin_contact=self.superuser,
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER)
        a1.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1,
            }), {'resolution': 'q'}, follow=True)
        self.assertContains(response, 'Received invalid resolution type')

    def test_cant_resolve_others_applications(self):
        a1 = Application(
            admin_contact=self.content_mod,
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER)
        a1.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1,
            }), {'resolution': 'a'}, follow=True)
        self.assertContains(response, 'Only the admin contact may resolve '
                            'this application')

    def test_can_resolve_all_applications(self):
        a1 = Application(
            admin_contact=self.superuser,
            applicant=self.user,
            application_type=Application.CLAIM_PUBLISHER)
        a1.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 1,
            }), {'resolution': 'a'}, follow=True)
        self.assertContains(response, 'The application has been resolved.')
        a1.refresh_from_db()
        self.assertEqual(a1.resolution, 'a')
        a2 = Application(
            admin_contact=self.superuser,
            applicant=self.user,
            application_type=Application.AD)
        a2.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_application', kwargs={
                'application_id': 2,
            }), {'resolution': 'a'}, follow=True)
        self.assertContains(response, 'The application has been resolved.')
        a2.refresh_from_db()
        self.assertEqual(a2.resolution, 'a')
