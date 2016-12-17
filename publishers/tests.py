import mock
from PIL import Image

from django.contrib.auth.models import (
    Group,
    User,
)
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from submitify.models import Call

from .models import (
    NewsItem,
    Publisher,
)
from .views import set_group_membership
from usermgmt.models import Profile


class BasePublisherTestCase(TestCase):
    fixtures = ['groups.json']

    @classmethod
    def setUpTestData(cls):
        content_moderators = Group.objects.get(name='Content moderators')
        cls.admin = User.objects.create_user(
            'admin',
            'admin@example.com',
            'admin pass')
        cls.admin.profile = Profile()
        cls.admin.profile.save()
        cls.admin.groups.add(content_moderators)
        cls.owner = User.objects.create_user(
            'owner',
            'owner@example.com',
            'owner pass')
        cls.owner.profile = Profile()
        cls.owner.profile.save()
        cls.editor = User.objects.create_user(
            'editor',
            'editor@example.com',
            'editor pass')
        cls.editor.profile = Profile()
        cls.editor.profile.save()
        cls.member = User.objects.create_user(
            'member',
            'member@example.com',
            'member pass')
        cls.member.profile = Profile()
        cls.member.profile.save()
        cls.user = User.objects.create_user(
            'user',
            'user@example.com',
            'user pass')
        cls.user.profile = Profile()
        cls.user.profile.save()

        with mock.patch.object(Image, 'open'):
            cls.unowned_publisher = Publisher(
                name='Unowned publisher',
                url='http://example.com',
                logo='icon.png',
                banner='banner.png',
                body_raw='*Unowned* publisher')
            cls.unowned_publisher.save()
            cls.owned_publisher = Publisher(
                owner=cls.owner,
                name='Owned publisher',
                url='http://example.com',
                logo='icon.png',
                banner='banner.png',
                body_raw='*Owned* publisher')
            cls.owned_publisher.save()
            cls.news_item = NewsItem(
                publisher=cls.owned_publisher,
                owner=cls.editor,
                image='image.png',
                subject='News from the publisher',
                body_raw='*Newsworthy* news')
            cls.news_item.save()

        cls.owned_publisher.editors.add(cls.owner)
        cls.owned_publisher.editors.add(cls.editor)
        cls.owned_publisher.members.add(cls.member)
        set_group_membership(cls.owner)
        set_group_membership(cls.editor)
        set_group_membership(cls.member)
        set_group_membership(cls.user)

        cls.owned_call = Call(
            owner=cls.owner,
            status=Call.OPEN,
            title='Owned call',
            about_raw='Testing',
            genre='test',
            length='1000-5000')
        cls.owned_call.save()
        cls.owned_publisher.calls.add(cls.owned_call)
        cls.unowned_call = Call(
            owner=cls.editor,
            status=Call.OPEN,
            title='Unowned call',
            about_raw='Testing',
            genre='test',
            length='1000-5000')
        cls.unowned_call.save()
        cls.unownable_call = Call(
            owner=cls.user,
            status=Call.OPEN,
            title='Unownable call',
            about_raw='Testing',
            genre='test',
            length='1000-5000')
        cls.unownable_call.save()


class PublisherModelTestCase(BasePublisherTestCase):
    def test_markdown_body(self):
        self.assertEqual(self.owned_publisher.body_rendered,
                         '<p><em>Owned</em> publisher</p>')

    def test_image_resize(self):
        with mock.patch.object(Image, 'open') as mock_open:
            image = mock_open.return_value
            self.owned_publisher.save()
        self.assertEqual(mock_open.call_count, 2)
        self.assertEqual(image.thumbnail.call_count, 2)
        self.assertEqual(image.save.call_count, 2)
        image.thumbnail.assert_has_calls([
            mock.call((500, 500), Image.ANTIALIAS),
            mock.call((2048, 2048), Image.ANTIALIAS),
        ])

    def test_get_absolute_url(self):
        self.assertEqual(
            self.owned_publisher.get_absolute_url(),
            reverse('publishers:view_publisher', kwargs={
                'publisher_slug': 'owned-publisher',
            }))


class NewsItemModelTestCase(BasePublisherTestCase):
    def test_markdown_body(self):
        self.assertEqual(self.news_item.body_rendered,
                         '<p><em>Newsworthy</em> news</p>')

    def test_image_resize(self):
        with mock.patch.object(Image, 'open') as mock_open:
            image = mock_open.return_value
            self.news_item.save()
        self.assertEqual(mock_open.call_count, 1)
        self.assertEqual(image.thumbnail.call_count, 1)
        self.assertEqual(image.save.call_count, 1)
        image.thumbnail.assert_called_once_with(
            (2048, 2048), Image.ANTIALIAS)

    def test_get_absolute_url(self):
        self.assertEqual(
            self.news_item.get_absolute_url(),
            reverse('publishers:view_news_item', kwargs={
                'publisher_slug': 'owned-publisher',
                'item_id': 1,
            }))


class ListPublishersViewTestCase(BasePublisherTestCase):
    def test_lists(self):
        response = self.client.get(reverse('publishers:list_publishers'))
        self.assertContains(response, '<p><em>Owned</em> publisher</p>')
        self.assertNotContains(response, '<p><em>Unowned</em> publisher</p>')

    def test_lists_without_owners_if_admin(self):
        self.client.login(username='admin', password='admin pass')
        response = self.client.get(reverse('publishers:list_publishers'))
        self.assertContains(response, '<p><em>Owned</em> publisher</p>')
        self.assertContains(response, '<p><em>Unowned</em> publisher</p>')

    def test_doesnt_list_without_owners_if_not_admin(self):
        self.client.login(username='user', password='user pass')
        response = self.client.get(reverse('publishers:list_publishers'))
        self.assertContains(response, '<p><em>Owned</em> publisher</p>')
        self.assertNotContains(response, '<p><em>Unowned</em> publisher</p>')

    def test_paginates(self):
        for i in range(1, 30):
            with mock.patch.object(Image, 'open'):
                Publisher(
                    owner=self.owner,
                    name='Owned publisher {}'.format(i),
                    url='http://example.com',
                    logo='icon.png',
                    banner='banner.png',
                    body_raw='*Owned* publisher').save()
        response = self.client.get(reverse('publishers:list_publishers'))
        self.assertContains(response, '2/">2</a>')
        self.assertNotContains(response, '3/">3</a>')

    def test_respects_users_results_per_page(self):
        for i in range(1, 30):
            with mock.patch.object(Image, 'open'):
                Publisher(
                    owner=self.owner,
                    name='Owned publisher {}'.format(i),
                    url='http://example.com',
                    logo='icon.png',
                    banner='banner.png',
                    body_raw='*Owned* publisher').save()
        self.user.profile.results_per_page = 10
        self.user.profile.save()
        self.client.login(username='user', password='user pass')
        response = self.client.get(reverse('publishers:list_publishers'))
        self.assertContains(response, '2/">2</a>')
        self.assertContains(response, '3/">3</a>')


class CreatePublisherViewTestCase(BasePublisherTestCase):
    def test_permission_denied(self):
        self.client.login(username='user', password='user pass')
        response = self.client.get(reverse('publishers:create_publisher'))
        self.assertEqual(response.status_code, 302)

    def test_renders_form(self):
        self.client.login(username='admin', password='admin pass')
        response = self.client.get(reverse('publishers:create_publisher'))
        self.assertContains(response, 'Create publisher')

    @mock.Mock(spec=File)
    def test_creates_publisher(self, mock_file):
        self.client.login(username='admin', password='admin pass')
        with mock.patch.object(Image, 'open') as mock_open:
            response = self.client.post(
                reverse('publishers:create_publisher'),
                {
                    'name': 'New publisher',
                    'url': 'http://example.com/new',
                    'body_raw': 'A brand new publisher, publishing words',
                    'logo': SimpleUploadedFile('logo.png', b'logo data',
                                               content_type='image/png')
                },
                follow=True)
        self.assertTrue(mock_open.called)
        self.assertContains(response, 'New publisher')
        self.assertEqual(
            response.redirect_chain,
            [(reverse('publishers:view_publisher',
                      kwargs={'publisher_slug': 'new-publisher'}), 302)])


class ViewPublisherViewTestCase(BasePublisherTestCase):
    def renders_publisher(self):
        response = self.client.get(
            reverse('publishers:view_publisher', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertContains(response, '<em>Owned</em> publisher')

    def test_renders_without_owner_if_admin(self):
        self.client.login(username='admin', password='admin pass')
        response = self.client.get(
            reverse('publishers:view_publisher', kwargs={
                'publisher_slug': self.unowned_publisher.slug
            }))
        self.assertContains(response, '<em>Unowned</em> publisher')

    def test_doesnt_render_without_owner_if_not_admin(self):
        self.client.login(username='user', password='user pass')
        response = self.client.get(
            reverse('publishers:view_publisher', kwargs={
                'publisher_slug': self.unowned_publisher.slug
            }))
        self.assertEqual(response.status_code, 403)


class EditPublisherViewTestCase(BasePublisherTestCase):
    def test_permission_denied(self):
        self.client.login(username='user', password='user pass')
        response = self.client.get(
            reverse('publishers:edit_publisher', kwargs={
                'publisher_slug': self.owned_publisher.slug
            }))
        self.assertEqual(response.status_code, 403)

    def test_renders_form(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.get(
            reverse('publishers:edit_publisher', kwargs={
                'publisher_slug': self.owned_publisher.slug
            }))
        self.assertContains(response, 'Edit publisher')

    @mock.Mock(spec=File)
    def test_edits_publisher(self, mock_file):
        self.client.login(username='owner', password='owner pass')
        with mock.patch.object(Image, 'open') as mock_open:
            response = self.client.get(
                reverse('publishers:edit_publisher', kwargs={
                    'publisher_slug': self.owned_publisher.slug
                }),
                {
                    'name': 'New publisher',
                    'url': 'http://example.com/new',
                    'body_raw': 'A brand new publisher, publishing words',
                    'logo': SimpleUploadedFile('logo.png', b'logo data',
                                               content_type='image/png')
                },
                follow=True)
        self.assertTrue(mock_open.called)
        self.assertContains(response, 'New publisher')
        self.assertEqual(
            response.redirect_chain,
            [(reverse('publishers:view_publisher',
                      kwargs={'publisher_slug': 'new-publisher'}), 302)])


class DeletePublisherViewTestCase(BasePublisherTestCase):
    def test_permission_denied(self):
        self.client.login(username='user', password='user pass')
        response = self.client.get(
            reverse('publishers:delete_publisher', kwargs={
                'publisher_slug': self.owned_publisher.slug
            }))
        self.assertEqual(response.status_code, 302)

    def test_renders_confirmation(self):
        self.client.login(username='admin', password='admin pass')
        response = self.client.get(
            reverse('publishers:delete_publisher', kwargs={
                'publisher_slug': self.owned_publisher.slug
            }))
        self.assertContains(response, 'You are about to delete this publisher')

    def test_deletes_publisher(self):
        self.client.login(username='admin', password='admin pass')
        response = self.client.post(
            reverse('publishers:delete_publisher', kwargs={
                'publisher_slug': self.owned_publisher.slug
            }), follow=True)
        self.assertContains(response, 'Publisher deleted')


class AddMemberViewTestCase(BasePublisherTestCase):
    def test_permission_denied(self):
        self.client.login(username='user', password='user pass')
        response = self.client.post(
            reverse('publishers:add_member', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'member',
            }, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_adds_member(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:add_member', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'user',
            }, follow=True)
        self.assertContains(response, 'User added to members')

    def test_member_already_added(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:add_member', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'member',
            }, follow=True)
        self.assertContains(response, 'User already in members')


class RemoveMemberViewTestCase(BasePublisherTestCase):
    def test_permission_denied(self):
        self.client.login(username='user', password='user pass')
        response = self.client.post(
            reverse('publishers:remove_member', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'user',
            }, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_adds_member(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:remove_member', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'member',
            }, follow=True)
        self.assertContains(response, 'User removed from members')

    def test_member_already_added(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:remove_member', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'user',
            }, follow=True)
        self.assertContains(response, 'User not in members')


class AddEditorViewTestCase(BasePublisherTestCase):
    def test_permission_denied(self):
        self.client.login(username='user', password='user pass')
        response = self.client.post(
            reverse('publishers:add_editor', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'editor',
            }, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_adds_editor(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:add_editor', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'user',
            }, follow=True)
        self.assertContains(response, 'User added to editors')

    def test_editor_already_added(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:add_editor', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'editor',
            }, follow=True)
        self.assertContains(response, 'User already in editors')


class RemoveEditorViewTestCase(BasePublisherTestCase):
    def test_permission_denied(self):
        self.client.login(username='user', password='user pass')
        response = self.client.post(
            reverse('publishers:remove_editor', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'user',
            }, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_adds_editor(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:remove_editor', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'editor',
            }, follow=True)
        self.assertContains(response, 'User removed from editors')

    def test_editor_already_added(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:remove_editor', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'user',
            }, follow=True)
        self.assertContains(response, 'User not in editors')


class ListCallsViewTestCase(BasePublisherTestCase):
    def test_lists_calls_with_filters(self):
        self.owned_call.status = Call.NOT_OPEN_YET
        self.owned_call.save()
        response = self.client.get(
            reverse('publishers:list_calls', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertNotContains(response, 'Owned call')
        response = self.client.get(
            reverse('publishers:list_calls', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }), {'opening-soon': 1})
        self.assertContains(response, 'Owned call')

    def test_lists_available_calls(self):
        response = self.client.get(
            reverse('publishers:list_calls', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertContains(response, 'Owned call')


class AddCallViewTestCase(BasePublisherTestCase):
    def test_only_owner(self):
        self.client.login(username='editor', password='editor pass')
        response = self.client.post(
            reverse('publishers:add_call', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'call_id': self.unowned_call.id,
            },
            follow=True)
        self.assertTrue(response.status_code, 403)

    def test_only_editor_calls(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:add_call', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'call_id': self.unownable_call.id,
            },
            follow=True)
        self.assertTrue(response.status_code, 403)

    def test_call_already_added(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:add_call', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'call_id': self.owned_call.id,
            },
            follow=True)
        self.assertContains(response, 'already owns this call')

    def test_adds_call(self):
        self.client.login(username='owner', password='owner pass')
        self.client.post(
            reverse('publishers:add_call', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'call_id': self.unowned_call.id,
            },
            follow=True)
        self.assertEqual(self.owned_publisher.calls.count(), 2)


class RemoveCallViewTestCase(BasePublisherTestCase):
    def test_only_owner(self):
        self.client.login(username='editor', password='editor pass')
        response = self.client.post(
            reverse('publishers:remove_call', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'call_id': self.owned_call.id,
            },
            follow=True)
        self.assertTrue(response.status_code, 403)

    def test_call_not_owned(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:remove_call', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'call_id': self.unowned_call.id,
            },
            follow=True)
        self.assertContains(response, "doesn't own this call")

    def test_removes_call(self):
        self.client.login(username='owner', password='owner pass')
        self.client.post(
            reverse('publishers:remove_call', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'call_id': self.owned_call.id,
            },
            follow=True)
        self.assertEqual(self.owned_publisher.calls.count(), 0)


class ChangeOwnershipViewTestCase(BasePublisherTestCase):
    @mock.patch.object(Image, 'open')
    def test_changes_ownership(self, mock_open):
        self.client.login(username='admin', password='admin pass')
        self.client.post(
            reverse('publishers:change_ownership', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'username': 'editor',
            },
            follow=True)
        self.owned_publisher.refresh_from_db()
        self.assertEqual(self.owned_publisher.owner.username, 'editor')


class ListNewsItemsViewTestCase(BasePublisherTestCase):
    def test_lists_news_items(self):
        response = self.client.get(
            reverse('publishers:list_news_items', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertContains(response, 'News from the publisher')

    def test_paginates(self):
        for i in range(1, 30):
            NewsItem(
                publisher=self.owned_publisher,
                owner=self.editor,
                subject='News item {}'.format(i),
                body_raw='*Newsworthy* news').save()
        response = self.client.get(
            reverse('publishers:list_news_items', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertContains(response, '2/">2<')

    def test_respects_users_results_per_page(self):
        for i in range(1, 30):
            NewsItem(
                publisher=self.owned_publisher,
                owner=self.editor,
                subject='News item {}'.format(i),
                body_raw='*Newsworthy* news').save()
        self.user.profile.results_per_page = 10
        self.user.profile.save()
        self.client.login(username='user', password='user pass')
        response = self.client.get(
            reverse('publishers:list_news_items', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertContains(response, '2/">2<')
        self.assertContains(response, '3/">3<')


class CreateNewsItemViewTestCase(BasePublisherTestCase):
    def test_only_editors(self):
        self.client.login(username='member', password='member pass')
        response = self.client.get(
            reverse('publishers:create_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertEqual(response.status_code, 403)

    def test_renders_form(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.get(
            reverse('publishers:create_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }))
        self.assertContains(response, 'Create news item')

    def test_creates_news_item(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:create_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
            }),
            {
                'subject': 'Brand spanking new',
                'body_raw': 'New new new',
            }, follow=True)
        self.assertContains(response, 'Brand spanking new')


class ViewNewsItemTestCase(BasePublisherTestCase):
    def test_renders_news_item(self):
        response = self.client.get(self.news_item.get_absolute_url())
        self.assertContains(response, '<em>Newsworthy</em> news')


class EditNewsItemViewTestCase(BasePublisherTestCase):
    def test_shortcut_noneditors_forbidden(self):
        self.client.login(username='member', password='member pass')
        response = self.client.get(
            reverse('publishers:edit_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id,
            }))
        self.assertEqual(response.status_code, 403)

    def test_item_owner_or_publisher_owner_only(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.get(
            reverse('publishers:edit_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.client.login(username='editor', password='editor pass')
        response = self.client.get(
            reverse('publishers:edit_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertEqual(response.status_code, 200)
        self.news_item.owner = self.owner
        with mock.patch.object(Image, 'open'):
            self.news_item.save()
        response = self.client.get(
            reverse('publishers:edit_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertEqual(response.status_code, 403)

    def test_renders_form(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.get(
            reverse('publishers:edit_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertContains(response, 'Edit news item')

    @mock.patch.object(Image, 'open')
    def test_edits_news_item(self, mock_open):
        self.client.login(username='owner', password='owner pass')
        response = self.client.post(
            reverse('publishers:edit_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id,
            }),
            {
                'subject': 'Brand spanking new',
                'body_raw': 'New new new',
            }, follow=True)
        self.assertContains(response, 'Brand spanking new')


class DeleteNewsItemViewTestCase(BasePublisherTestCase):
    def test_shortcut_noneditors_forbidden(self):
        self.client.login(username='member', password='member pass')
        response = self.client.get(
            reverse('publishers:delete_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id,
            }))
        self.assertEqual(response.status_code, 403)

    def test_item_owner_or_publisher_owner_only(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.get(
            reverse('publishers:delete_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.client.login(username='editor', password='editor pass')
        response = self.client.get(
            reverse('publishers:delete_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertEqual(response.status_code, 200)
        self.news_item.owner = self.owner
        with mock.patch.object(Image, 'open'):
            self.news_item.save()
        response = self.client.get(
            reverse('publishers:delete_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertEqual(response.status_code, 403)

    def test_renders_confirmation(self):
        self.client.login(username='owner', password='owner pass')
        response = self.client.get(
            reverse('publishers:delete_news_item', kwargs={
                'publisher_slug': self.owned_publisher.slug,
                'item_id': self.news_item.id
            }))
        self.assertContains(response, 'You are about to delete this news item')

    def test_deletes_news_item(self):
        def test_edits_news_item(self):
            self.client.login(username='owner', password='owner pass')
            response = self.client.post(
                reverse('publishers:delete_news_item', kwargs={
                    'publisher_slug': self.owned_publisher.slug,
                    'item_id': self.news_item.id,
                }), {}, follow=True)
            self.assertContains(response, 'News item deleted')


class SetGroupMembershipUtilityTestCase(BasePublisherTestCase):
    def test_adds_group(self):
        self.assertEqual(self.member.groups.count(), 0)
        self.owned_publisher.editors.add(self.member)
        set_group_membership(self.member)
        self.assertEqual(self.member.groups.count(), 1)

    def test_removes_group(self):
        self.assertEqual(self.editor.groups.count(), 1)
        self.owned_publisher.editors.remove(self.editor)
        set_group_membership(self.editor)
        self.assertEqual(self.editor.groups.count(), 0)
