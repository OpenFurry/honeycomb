import mock

from django.core.urlresolvers import reverse
from django.test import tag
from django.utils import timezone
from taggit.models import Tag

from .models import Flag
from .tests import BaseAdminTestCase
from submissions.tests import SubmissionsViewsBaseTestCase
from usermgmt import models as usermodels


class BaseFlagTestCase(BaseAdminTestCase, SubmissionsViewsBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super(BaseFlagTestCase, cls).setUpTestData()


@tag('as_user')
class TestListAllFlagsViewAsUser(BaseFlagTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:list_all_flags'))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestListAllFlagsViewAsSocialMod(BaseFlagTestCase):
    def test_forbidden(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:list_all_flags'))
        self.assertEqual(response.status_code, 403)


@tag('as_content_mod')
class TestListAllFlagsViewAsContentMod(BaseFlagTestCase):
    def test_forbidden(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:list_all_flags'))
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestListAllFlagsViewAsSuperuser(BaseFlagTestCase):
    def test_lists_flags(self):
        Flag(
            flag_type=Flag.SOCIAL,
            flagged_by=self.user,
            object_model=self.submission1,
            subject='bad submission',
            body_raw='bad to the bone, really').save()
        Flag(
            flag_type=Flag.CONTENT,
            flagged_by=self.user,
            object_model=self.submission2,
            subject='kinda gross',
            body_raw='who even does that').save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:list_all_flags'))
        self.assertContains(response, 'bad submission')
        self.assertContains(response, 'kinda gross')

    def test_lists_inactive_flags(self):
        Flag(
            flag_type=Flag.SOCIAL,
            flagged_by=self.user,
            object_model=self.submission1,
            subject='bad submission',
            body_raw='bad to the bone, really').save()
        Flag(
            flag_type=Flag.CONTENT,
            flagged_by=self.user,
            object_model=self.submission2,
            resolved=timezone.now(),
            subject='kinda gross',
            body_raw='who even does that').save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:list_all_flags'), {
            'all': 1,
        })
        self.assertContains(response, 'bad submission')
        self.assertContains(response, 'kinda gross')


@tag('as_user')
class TestListSocialFlagsViewAsUser(BaseFlagTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_social_flags'))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestListSocialFlagsViewAsSocialMod(BaseFlagTestCase):
    def test_lists_social_flags(self):
        Flag(
            flag_type=Flag.SOCIAL,
            flagged_by=self.user,
            object_model=self.submission1,
            subject='bad submission',
            body_raw='bad to the bone, really').save()
        Flag(
            flag_type=Flag.CONTENT,
            flagged_by=self.user,
            object_model=self.submission2,
            subject='kinda gross',
            body_raw='who even does that').save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(
            reverse('administration:list_social_flags'))
        self.assertContains(response, 'bad submission')
        self.assertNotContains(response, 'kinda gross')


@tag('as_content_mod')
class TestListSocialFlagsViewAsContentMod(BaseFlagTestCase):
    def test_forbidden(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:list_social_flags'))
        self.assertEqual(response.status_code, 403)


@tag('as_superuser')
class TestListSocialFlagsViewAsSuperuser(BaseFlagTestCase):
    def test_lists_content_flags(self):
        Flag(
            flag_type=Flag.SOCIAL,
            flagged_by=self.user,
            object_model=self.submission1,
            subject='bad submission',
            body_raw='bad to the bone, really').save()
        Flag(
            flag_type=Flag.CONTENT,
            flagged_by=self.user,
            object_model=self.submission2,
            subject='kinda gross',
            body_raw='who even does that').save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(
            reverse('administration:list_social_flags'))
        self.assertContains(response, 'bad submission')
        self.assertNotContains(response, 'kinda gross')


@tag('as_user')
class TestListContentFlagsViewAsUser(BaseFlagTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse(
            'administration:list_content_flags'))
        self.assertEqual(response.status_code, 403)


@tag('as_social_mod')
class TestListContentFlagsViewAsSocialMod(BaseFlagTestCase):
    def test_forbidden(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse(
            'administration:list_content_flags'))
        self.assertEqual(response.status_code, 403)


@tag('as_content_mod')
class TestListContentFlagsViewAsContentMod(BaseFlagTestCase):
    def test_lists_content_flags(self):
        Flag(
            flag_type=Flag.SOCIAL,
            flagged_by=self.user,
            object_model=self.submission1,
            subject='bad submission',
            body_raw='bad to the bone, really').save()
        Flag(
            flag_type=Flag.CONTENT,
            flagged_by=self.user,
            object_model=self.submission2,
            subject='kinda gross',
            body_raw='who even does that').save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(
            reverse('administration:list_content_flags'))
        self.assertNotContains(response, 'bad submission')
        self.assertContains(response, 'kinda gross')


@tag('as_superuser')
class TestListContentFlagsViewAsSuperuser(BaseFlagTestCase):
    def test_lists_content_flags(self):
        Flag(
            flag_type=Flag.SOCIAL,
            flagged_by=self.user,
            object_model=self.submission1,
            subject='bad submission',
            body_raw='bad to the bone, really').save()
        Flag(
            flag_type=Flag.CONTENT,
            flagged_by=self.user,
            object_model=self.submission2,
            subject='kinda gross',
            body_raw='who even does that').save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(
            reverse('administration:list_content_flags'))
        self.assertNotContains(response, 'bad submission')
        self.assertContains(response, 'kinda gross')


class TestCreateFlagView(BaseFlagTestCase):
    def test_requires_content_type_and_id(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:create_flag'))
        self.assertEqual(response.status_code, 403)

    def test_restricted_content_types(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:create_flag'), {
            'content_type': 'auth:user',
            'object_id': 1,
        })
        self.assertEqual(response.status_code, 403)

    def test_cant_flag_own_object(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('administration:create_flag'), {
            'content_type': 'submissions:submission',
            'object_id': self.submission1.id,
        })
        self.assertEqual(response.status_code, 403)

    def test_renders_form(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:create_flag'), {
            'content_type': 'submissions:submission',
            'object_id': self.submission1.id,
        })
        self.assertContains(response, 'Flag submission')
        self.assertContains(response, 'Submission 1 by ~foo')

    def test_creates_flag_with_owner(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(
            reverse('administration:create_flag'), {
                'content_type': 'submissions:submission',
                'object_id': self.submission1.id,
                'flag_type': Flag.CONTENT,
                'subject': 'it is bad',
                'body_raw': 'i did not like it, *no sir*',
            }, follow=True)
        self.assertContains(response, "User McUserface's flag")
        self.assertContains(response, 'Submission 1 by ~foo')

    def test_creates_flag_with_user(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(
            reverse('administration:create_flag'), {
                'content_type': 'usermgmt:profile',
                'object_id': self.social_mod.profile.id,
                'flag_type': Flag.CONTENT,
                'subject': 'it is bad',
                'body_raw': 'i did not like it, *no sir*',
            }, follow=True)
        self.assertContains(response, "User McUserface's flag")

    def test_creates_flag_without_owner(self):
        tag = Tag(name='Test tag')
        tag.save()
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(
            reverse('administration:create_flag'), {
                'content_type': 'taggit:tag',
                'object_id': tag.id,
                'flag_type': Flag.CONTENT,
                'subject': 'it is bad',
                'body_raw': 'i did not like it, *no sir*',
            }, follow=True)
        self.assertContains(response, "User McUserface's flag")


class ExistingFlagBaseTestCase(BaseFlagTestCase):
    @classmethod
    def setUpTestData(cls):
        super(ExistingFlagBaseTestCase, cls).setUpTestData()
        cls.active_content_flag = Flag(
            flagged_by=cls.bar,
            object_model=cls.submission1,
            flagged_object_owner=cls.user,
            flag_type=Flag.CONTENT,
            subject='user + submission1 + content + active',
            body_raw='Test flag')
        cls.active_content_flag.save()
        cls.active_social_flag = Flag(
            flagged_by=cls.bar,
            object_model=cls.foo.profile,
            flagged_object_owner=cls.foo,
            flag_type=Flag.SOCIAL,
            subject='foo + foo.profile + social + active',
            body_raw='Test flag')
        cls.active_social_flag.save()


class ModelTestCase(ExistingFlagBaseTestCase):
    def test_str(self):
        self.assertEqual(
            self.active_content_flag.__str__(),
            'user + submission1 + content + active (against Submission 1 by '
            '~foo (id:1))')

    def test_unicode(self):
        self.assertEqual(
            self.active_content_flag.__unicode__(),
            'user + submission1 + content + active (against Submission 1 by '
            '~foo (id:1))')


@tag('as_user')
class TestViewFlagViewAsUser(ExistingFlagBaseTestCase):
    def test_forbidden_unless_participant(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_social_flag.id
        }))
        self.assertEqual(response.status_code, 403)

    def test_renders_flag_if_participant(self):
        self.active_content_flag.participants.add(self.user)
        self.client.login(username='user',
                          password='user pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_content_flag.id
        }))
        self.assertContains(response, 'user + submission1 + content + active')


@tag('as_social_mod')
class TestViewFlagViewAsSocialMod(ExistingFlagBaseTestCase):
    def test_content_flag_forbidden_unless_participant(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_content_flag.id
        }))
        self.assertEqual(response.status_code, 403)

    def test_renders_content_flag_if_participant(self):
        self.active_content_flag.participants.add(self.social_mod)
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_content_flag.id
        }))
        self.assertContains(response, 'user + submission1 + content + active')

    def test_renders_social_flag(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_social_flag.id
        }))
        self.assertContains(response, 'foo + foo.profile + social + active')


@tag('as_content_mod')
class TestViewFlagViewAsContentMod(ExistingFlagBaseTestCase):
    def test_social_flag_forbidden_unless_participant(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_social_flag.id
        }))
        self.assertEqual(response.status_code, 403)

    def test_renders_social_flag_if_participant(self):
        self.active_social_flag.participants.add(self.content_mod)
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_social_flag.id
        }))
        self.assertContains(response, 'foo + foo.profile + social + active')

    def test_renders_content_flag(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_content_flag.id
        }))
        self.assertContains(response, 'user + submission1 + content + active')


@tag('as_superuser')
class TestViewFlagViewAsSuperuser(ExistingFlagBaseTestCase):
    def test_renders_flag(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_content_flag.id
        }))
        self.assertContains(response, 'user + submission1 + content + active')
        response = self.client.get(reverse('administration:view_flag', kwargs={
            'flag_id': self.active_social_flag.id
        }))
        self.assertContains(response, 'foo + foo.profile + social + active')


class TestListParticipatingFlagsView(ExistingFlagBaseTestCase):
    def test_renders_no_flags(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:list_participating_flags'))
        self.assertContains(response, 'No flags to display')

    def test_renders_own_flags(self):
        self.active_social_flag.participants.add(self.content_mod)
        self.active_content_flag.participants.add(self.content_mod)
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.get(reverse(
            'administration:list_participating_flags'))
        self.assertContains(response, 'foo + foo.profile + social + active')
        self.assertContains(response, 'user + submission1 + content + active')


@tag('as_user')
class TestJoinFlagViewAsUser(ExistingFlagBaseTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response, 'not authorized to access this page')


@tag('as_social_mod')
class TestJoinFlagViewAsSocialMod(ExistingFlagBaseTestCase):
    def test_joining_content_flag_forbidden(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_cant_join_resolved_flag(self):
        self.active_social_flag.resolved = timezone.now()
        self.active_social_flag.save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_warn_if_already_participant(self):
        self.active_social_flag.participants.add(self.social_mod)
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You are already a participant in this flag')

    def test_join_flag(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You are now a participant in this flag')


@tag('as_content_mod')
class TestJoinFlagViewAsContentMod(ExistingFlagBaseTestCase):
    def test_joining_social_flag_forbidden(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_cant_join_resolved_flag(self):
        self.active_content_flag.resolved = timezone.now()
        self.active_content_flag.save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_warn_if_already_participant(self):
        self.active_content_flag.participants.add(self.content_mod)
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You are already a participant in this flag')

    def test_join_flag(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You are now a participant in this flag')


@tag('as_superuser')
class TestJoinFlagViewAsSuperuser(ExistingFlagBaseTestCase):
    def test_cant_join_resolved_flag(self):
        self.active_social_flag.resolved = timezone.now()
        self.active_social_flag.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_warn_if_already_participant(self):
        self.active_social_flag.participants.add(self.superuser)
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You are already a participant in this flag')

    @mock.patch.object(usermodels, 'Notification')
    def test_join_flag(self, mock_notification):
        self.active_social_flag.participants.add(self.user)
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:join_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You are now a participant in this flag')
        self.assertTrue(mock_notification.called_once)


@tag('as_user')
class TestResolveFlagViewAsUser(ExistingFlagBaseTestCase):
    def test_forbidden(self):
        self.client.login(username='user',
                          password='user pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response, 'not authorized to access this page')


@tag('as_social_mod')
class TestResolveFlagViewAsSocialMod(ExistingFlagBaseTestCase):
    def test_resolving_content_flag_forbidden(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_resolving_resolved_flag_forbidden(self):
        self.active_social_flag.resolved = timezone.now()
        self.active_social_flag.save()
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_cant_resolve_flag_not_participating_in(self):
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You must be participating in this flag')

    def test_require_resolution(self):
        self.active_social_flag.participants.add(self.social_mod)
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response, 'You must provide a resolution')

    def test_flag_resolved(self):
        self.active_social_flag.participants.add(self.social_mod)
        self.client.login(username='social_mod',
                          password='social_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), {'resolution': 'done'}, follow=True)
        self.assertContains(response, 'Flag resolved')


@tag('as_content_mod')
class TestResolveFlagViewAsContentMod(ExistingFlagBaseTestCase):
    def test_resolving_social_flag_forbidden(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_resolving_resolved_flag_forbidden(self):
        self.active_content_flag.resolved = timezone.now()
        self.active_content_flag.save()
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_cant_resolve_flag_not_participating_in(self):
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You must be participating in this flag')

    def test_require_resolution(self):
        self.active_content_flag.participants.add(self.content_mod)
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertContains(response, 'You must provide a resolution')

    def test_flag_resolved(self):
        self.active_content_flag.participants.add(self.content_mod)
        self.client.login(username='content_mod',
                          password='content_mod pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), {'resolution': 'done'}, follow=True)
        self.assertContains(response, 'Flag resolved')


@tag('as_superuser')
class TestResolveFlagViewAsSuperuser(ExistingFlagBaseTestCase):
    def test_resolving_resolved_flag_forbidden(self):
        self.active_social_flag.resolved = timezone.now()
        self.active_social_flag.save()
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_cant_resolve_flag_not_participating_in(self):
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_content_flag.id,
            }), follow=True)
        self.assertContains(response,
                            'You must be participating in this flag')

    def test_require_resolution(self):
        self.active_social_flag.participants.add(self.superuser)
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), follow=True)
        self.assertContains(response, 'You must provide a resolution')

    @mock.patch.object(usermodels, 'Notification')
    def test_flag_resolved(self, mock_notification):
        self.active_social_flag.participants.add(self.superuser)
        self.active_social_flag.participants.add(self.social_mod)
        self.client.login(username='superuser',
                          password='superuser pass')
        response = self.client.post(reverse(
            'administration:resolve_flag', kwargs={
                'flag_id': self.active_social_flag.id,
            }), {'resolution': 'done'}, follow=True)
        self.assertContains(response, 'Flag resolved')
        self.assertTrue(mock_notification.called_once)
