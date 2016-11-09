from django.core.urlresolvers import reverse
from django.test import tag
from django.utils import timezone

from .models import Ban
from .tests import BaseAdminTestCase


@tag('as_user')
class TestListBansViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:list_bans'))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestListBansViewAsSocialMod(BaseAdminTestCase):
    def test_no_bans(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:list_bans'))
        self.assertContains(response, 'No bans to display')

    def test_lists_active_bans(self):
        now = timezone.now()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            active=False).save()
        Ban(user=self.user,
            admin_contact=self.social_mod).save()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            end_date=now).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:list_bans'))
        self.assertContains(response, 'View inactive')
        self.assertNotContains(response, 'Inactive')
        self.assertContains(response, 'today')
        self.assertContains(response, 'Indefinite')
        self.assertContains(response, 'User McUserface', 2)

    def test_lists_all_bans(self):
        now = timezone.now()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            active=False).save()
        Ban(user=self.user,
            admin_contact=self.social_mod).save()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            end_date=now).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:list_bans'), {
            'all': 1,
        })
        self.assertContains(response, 'Hide inactive')
        self.assertContains(response, 'Inactive')
        self.assertContains(response, 'today')
        self.assertContains(response, 'Indefinite')
        self.assertContains(response, 'User McUserface', 3)


@tag('as_content_mod')
class TestListBansViewAsContentMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:list_bans'))
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestListBansViewAsSuperuser(BaseAdminTestCase):
    def test_no_bans(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:list_bans'))
        self.assertContains(response, 'No bans to display')

    def test_lists_active_bans(self):
        now = timezone.now()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            active=False).save()
        Ban(user=self.user,
            admin_contact=self.social_mod).save()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            end_date=now).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:list_bans'))
        self.assertContains(response, 'View inactive')
        self.assertNotContains(response, 'Inactive')
        self.assertContains(response, 'today')
        self.assertContains(response, 'Indefinite')
        self.assertContains(response, 'User McUserface', 2)

    def test_lists_all_bans(self):
        now = timezone.now()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            active=False).save()
        Ban(user=self.user,
            admin_contact=self.social_mod).save()
        Ban(user=self.user,
            admin_contact=self.social_mod,
            end_date=now).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:list_bans'), {
            'all': 1,
        })
        self.assertContains(response, 'Hide inactive')
        self.assertContains(response, 'Inactive')
        self.assertContains(response, 'today')
        self.assertContains(response, 'Indefinite')
        self.assertContains(response, 'User McUserface', 3)


@tag('as_user')
class TestCreateBanViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:create_ban'))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestCreateBanViewAsSocialMod(BaseAdminTestCase):
    def test_form_renders(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:create_ban'), {
            'user': 'user',
        })
        self.assertContains(response, 'End date')
        self.assertContains(response, 'Reason')
        self.assertContains(
            response,
            'This ban will go into effect <strong>immediately</strong>')

    def test_create_ban(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse('administration:create_ban'), {
            'user': self.user.id,
            'reason_raw': '*fooble*',
        }, follow=True)
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, 'Social Modface')
        self.assertContains(response, '<em>fooble</em>')
        ban = Ban.objects.get(pk=1)
        self.assertEqual(ban.admin_contact, self.social_mod)
        self.assertTrue(ban.user.profile.banned)

    def test_cant_ban_self(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:create_ban'), {
            'user': 'social_mod',
        })
        self.assertEqual(response.status_code, 403)

    def test_cant_ban_superuser(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:create_ban'), {
            'user': 'superuser',
        })
        self.assertEqual(response.status_code, 403)

    def test_cant_ban_inactive(self):
        self.user.is_active = False
        self.user.save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:create_ban'), {
            'user': 'user',
        })
        self.assertEqual(response.status_code, 403)


@tag('as_content_mod')
class TestCreateBanViewAsContentMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:create_ban'))
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestCreateBanViewAsSuperuser(BaseAdminTestCase):
    def test_form_renders(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:create_ban'), {
            'user': 'user',
        })
        self.assertContains(response, 'End date')
        self.assertContains(response, 'Reason')
        self.assertContains(
            response,
            'This ban will go into effect <strong>immediately</strong>')

    def test_create_ban(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse('administration:create_ban'), {
            'user': self.user.id,
            'reason_raw': '*fooble*',
        }, follow=True)
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, 'Super Q. User')
        self.assertContains(response, '<em>fooble</em>')
        ban = Ban.objects.get(pk=1)
        self.assertEqual(ban.admin_contact, self.superuser)
        self.assertTrue(ban.user.profile.banned)

    def test_cant_ban_self(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:create_ban'), {
            'user': 'superuser',
        })
        self.assertEqual(response.status_code, 403)

    def test_cant_ban_inactive(self):
        self.user.is_active = False
        self.user.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:create_ban'), {
            'user': 'user',
        })
        self.assertEqual(response.status_code, 403)


@tag('as_user')
class TestViewBanViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:view_ban', kwargs={
            'ban_id': 1,
        }))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestViewBanViewAsSocialMod(BaseAdminTestCase):
    def test_view_bans(self):
        now = timezone.now()
        b1 = Ban(user=self.user,
                 admin_contact=self.social_mod,
                 active=False)
        b1.save()
        b2 = Ban(user=self.user,
                 admin_contact=self.social_mod)
        b2.save()
        b3 = Ban(user=self.user,
                 admin_contact=self.superuser,
                 end_date=now)
        b3.save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(b1.get_absolute_url())
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, "Inactive")
        response = self.client.get(b2.get_absolute_url())
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, "Indefinite")
        response = self.client.get(b3.get_absolute_url())
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, "today")
        self.assertContains(response, "Super Q. User")


@tag('as_content_mod')
class TestViewBanViewAsContentMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:view_ban', kwargs={
            'ban_id': 1,
        }))
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestViewBanViewAsSuperuser(BaseAdminTestCase):
    def test_view_bans(self):
        now = timezone.now()
        b1 = Ban(user=self.user,
                 admin_contact=self.social_mod,
                 active=False)
        b1.save()
        b2 = Ban(user=self.user,
                 admin_contact=self.social_mod)
        b2.save()
        b3 = Ban(user=self.user,
                 admin_contact=self.superuser,
                 end_date=now)
        b3.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(b1.get_absolute_url())
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, "Inactive")
        self.assertContains(response, "Social Modface")
        response = self.client.get(b2.get_absolute_url())
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, "Indefinite")
        response = self.client.get(b3.get_absolute_url())
        self.assertContains(response, "User McUserface's ban")
        self.assertContains(response, "today")
        self.assertContains(response, "Super Q. User")


@tag('as_user')
class TestListParticipatingBansViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_participating_bans'))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestListParticipatingBansViewAsSocialMod(BaseAdminTestCase):
    def test_lists_own_bans(self):
        Ban(user=self.user,
            admin_contact=self.superuser).save()
        Ban(user=self.user,
            admin_contact=self.social_mod).save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:list_participating_bans'))
        self.assertContains(response, 'User McUserface', 1)


@tag('as_content_mod')
class TestListParticipatingBansViewAsContentMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_participating_bans'))
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestListParticipatingBansViewAsSuperuser(BaseAdminTestCase):
    def test_lists_own_bans(self):
        Ban(user=self.user,
            admin_contact=self.superuser).save()
        Ban(user=self.user,
            admin_contact=self.social_mod).save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse(
            'administration:list_participating_bans'))
        self.assertContains(response, 'User McUserface', 1)


@tag('as_user')
class TestLiftBanViewAsUser(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:lift_ban', kwargs={
            'ban_id': 1,
        }))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestLiftBanViewAsSocialMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:lift_ban', kwargs={
            'ban_id': 1,
        }))
        self.assertEqual(response.status_code, 403)


@tag('as_content_mod')
class TestLiftBanViewAsContentMod(BaseAdminTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:lift_ban', kwargs={
                'ban_id': 1,
            }))
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestLiftBanViewAsSuperuser(BaseAdminTestCase):
    def test_it_works(self):
        ban = Ban(user=self.user,
                  admin_contact=self.social_mod)
        ban.save()
        self.user.is_active = False
        self.user.save()
        self.user.profile.banned = True
        self.user.profile.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:lift_ban', kwargs={
                'ban_id': ban.id,
            }), follow=True)
        self.assertContains(response, 'Ban lifted.')
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        ban.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.profile.banned)
        self.assertFalse(ban.active)


@tag('as_user')
class TestBanNoticeView(BaseAdminTestCase):
    def test_ban_notice(self):
        Ban(user=self.user,
            reason_raw='bad-wolf',
            admin_contact=self.superuser).save()
        self.user.profile.banned = True
        self.user.profile.save()
        self.client.force_login(self.user)
        self.assertTrue(self.user.is_authenticated)
        response = self.client.get(reverse('core:front'), follow=True)
        self.assertContains(response, 'Your account has been disabled')
        self.assertContains(response, 'bad-wolf')
        self.assertContains(response, 'Super Q. User')
        self.assertContains(response, 'Log in')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_forbidden(self):
        b = Ban(user=self.user,
                reason_raw='bad-wolf',
                admin_contact=self.superuser)
        b.save()
        response = self.client.get(reverse(
            'administration:ban_notice', kwargs={
                'ban_id': b.id,
                'ban_hash': b.get_ban_hash(),
            }))
        self.assertEqual(response.status_code, 403)
        self.client.force_login(self.user)
        response = self.client.get(reverse(
            'administration:ban_notice', kwargs={
                'ban_id': b.id,
                'ban_hash': 'bad-wolf',
            }))
        self.assertEqual(response.status_code, 403)
