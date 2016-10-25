from django.core.urlresolvers import reverse

from .models import (
    Folder,
    FolderItem,
    Submission,
)
from .tests import SubmissionsViewsBaseTestCase


class SubmissionsFolderViewsBaseTestCase(SubmissionsViewsBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super(SubmissionsFolderViewsBaseTestCase, cls).setUpTestData()
        cls.folderA = Folder(
            owner=cls.foo,
            name='Folder A')
        cls.folderA.save()
        cls.folderB = Folder(
            owner=cls.foo,
            name='Folder B')
        cls.folderB.save()
        cls.folderC = Folder(
            owner=cls.foo,
            name='Folder C',
            parent=cls.folderB)
        cls.folderC.save()
        FolderItem(
            folder=cls.folderB,
            submission=cls.submission1,
            position=1).save()
        FolderItem(
            folder=cls.folderC,
            submission=cls.submission1,
            position=1).save()
        FolderItem(
            folder=cls.folderC,
            submission=cls.submission2,
            position=2).save()


class TestViewRootLevelFoldersView(SubmissionsFolderViewsBaseTestCase):
    def test_retrieves_only_root_level_folders(self):
        response = self.client.get(reverse(
            'submissions:view_root_level_folders', kwargs={
                'username': 'foo',
            }))
        self.assertContains(response, 'Folder A')
        self.assertContains(response, 'Folder B')
        self.assertNotContains(response, 'Folder C')

    def test_retrieves_folderless_submissions(self):
        submission = Submission(
            owner=self.foo,
            title='wahooo')
        submission.save()
        response = self.client.get(reverse(
            'submissions:view_root_level_folders', kwargs={
                'username': 'foo',
            }))
        self.assertContains(response, 'wahooo')
        self.assertNotContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_paginates_submissions(self):
        for i in range(1, 30):
            Submission(
                owner=self.foo,
                title='Submission {}'.format(i)).save()
        response = self.client.get(reverse(
            'submissions:view_root_level_folders', kwargs={
                'username': 'foo',
            }))
        self.assertContains(response, '<a href="{}">2</a>'.format(
            reverse('submissions:view_root_level_folders', kwargs={
                'username': 'foo',
                'page': 2,
            })))

    def test_paginates_submissions_respecting_user_settings(self):
        for i in range(1, 30):
            Submission(
                owner=self.foo,
                title='Submission {}'.format(i)).save()
        self.bar.profile.results_per_page = 10
        self.bar.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:view_root_level_folders', kwargs={
                'username': 'foo',
            }))
        self.assertContains(response, '<a href="{}">3</a>'.format(
            reverse('submissions:view_root_level_folders', kwargs={
                'username': 'foo',
                'page': 3,
            })))

    def test_paginates_submissions_resets_to_last_page(self):
        for i in range(1, 30):
            Submission(
                owner=self.foo,
                title='Submission {}'.format(i)).save()
        response = self.client.get(reverse(
            'submissions:view_root_level_folders', kwargs={
                'username': 'foo',
                'page': 42,
            }))
        self.assertContains(
            response,
            '2 <span class="sr-only">(current)</span>')


class TestViewFolderView(SubmissionsFolderViewsBaseTestCase):
    def test_view_folder_redirects_to_complete_url(self):
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
            }))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))

    def test_gets_only_direct_subfolders(self):
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertNotContains(response, 'Folder A')

    def test_displays_properly_with_no_subfolders(self):
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertNotContains(
            response, '<li class="list-group-item striped-item">')

    def test_retrieves_submissions_in_folder(self):
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderB.id,
                'folder_slug': self.folderB.slug,
            }))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_displays_properly_with_no_submissions(self):
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))
        self.assertContains(response, 'Showing results 0 through 0 of 0')

    def test_breadcrumbs(self):
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertContains(
            response, ('/<a href="{}"><em>{}</em></a>'
                       '/<em>{}</em>').format(
                           reverse('submissions:view_folder', kwargs={
                               'username': 'foo',
                               'folder_id': self.folderB.id,
                               'folder_slug': self.folderB.slug}),
                           self.folderB.name,
                           self.folderC.name))

    def test_paginates_submissions(self):
        for i in range(1, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission {}'.format(i))
            submission.save()
            FolderItem(
                folder=self.folderB,
                submission=submission,
                position=i).save()
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderB.id,
                'folder_slug': self.folderB.slug,
            }))
        self.assertContains(response, '<a href="{}">2</a>'.format(
            reverse('submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderB.id,
                'folder_slug': self.folderB.slug,
                'page': 2,
            })))

    def test_paginates_submissions_respecting_user_settings(self):
        for i in range(1, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission {}'.format(i))
            submission.save()
            FolderItem(
                folder=self.folderB,
                submission=submission,
                position=i).save()
        self.bar.profile.results_per_page = 10
        self.bar.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderB.id,
                'folder_slug': self.folderB.slug,
            }))
        self.assertContains(response, '<a href="{}">3</a>'.format(
            reverse('submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderB.id,
                'folder_slug': self.folderB.slug,
                'page': 3,
            })))

    def test_paginates_submissions_resets_to_last_page(self):
        for i in range(1, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission {}'.format(i))
            submission.save()
            FolderItem(
                folder=self.folderB,
                submission=submission,
                position=i).save()
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderB.id,
                'folder_slug': self.folderB.slug,
                'page': 42,
            }))
        self.assertContains(
            response,
            '2 <span class="sr-only">(current)</span>')

    def test_shows_controls_only_for_own_folder(self):
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertNotContains(response, 'Edit folder')
        self.assertNotContains(response, 'Sort submissions')
        self.assertNotContains(response, 'Delete folder')
        self.assertNotContains(response, 'New folder')
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertContains(response, 'Edit folder')
        self.assertContains(response, 'Sort submissions')
        self.assertContains(response, 'Delete folder')
        self.assertContains(response, 'New folder')


class TestCreateFolderView(SubmissionsFolderViewsBaseTestCase):
    def test_populates_folders_queryset(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:create_folder', kwargs={
                'username': 'foo',
            }))
        self.assertContains(response, 'Folder A</option>')
        self.assertContains(response, 'Folder B</option>')
        self.assertContains(response, 'Folder C</option>')

    def test_saves_folder_no_parent(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:create_folder', kwargs={
                'username': 'foo',
            }), {
                'name': 'Folder D',
                'parent': '',
            }, follow=True)
        self.assertContains(response, 'Folder D')
        self.assertContains(response, '<em>Parent folder</em>')
        self.assertContains(response, '<small>/<em>Folder D</em></small>')

    def test_saves_folder_parent(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:create_folder', kwargs={
                'username': 'foo',
            }), {
                'name': 'Folder D',
                'parent': '1',
            }, follow=True)
        self.assertContains(response, 'Folder D')
        self.assertContains(response, 'Parent folder: Folder A')
        self.assertNotContains(response, '<small>/<em>Folder D</em></small>')


class TestUpdateFolderView(SubmissionsFolderViewsBaseTestCase):
    def test_restricts_to_folder_owner(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:update_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))
        self.assertContains(response, "You can't update a folder that isn't "
                            "yours", status_code=403)

    def test_populates_folders_queryset(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:update_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))
        self.assertContains(response, 'Folder B</option>')
        self.assertContains(response, 'Folder C</option>')

    def test_saves_folder_no_parent(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:update_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }), {
                'name': 'Folder D',
                'parent': '',
            }, follow=True)
        self.assertContains(response, 'Folder D')
        self.assertContains(response, '<em>Parent folder</em>')
        self.assertContains(response, '<small>/<em>Folder D</em></small>')

    def test_saves_folder_parent(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:update_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }), {
                'name': 'Folder D',
                'parent': '2',
            }, follow=True)
        self.assertContains(response, 'Folder D')
        self.assertContains(response, 'Parent folder: Folder B')
        self.assertNotContains(response, '<small>/<em>Folder D</em></small>')


class TestDeleteFolderView(SubmissionsFolderViewsBaseTestCase):
    def test_restricts_to_folder_owner(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:delete_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))
        self.assertContains(response, "You can't delete a folder that isn't "
                            "yours", status_code=403)

    def test_ask_for_confirmation(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:delete_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))
        self.assertContains(response, 'You are about to delete your folder')

    def test_delete_on_confirmation(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:delete_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }), follow=True)
        self.assertContains(response, 'Folder deleted successfully.')

    def test_redirects_to_root(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:delete_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))
        self.assertEqual(response.url, reverse(
            'submissions:view_root_level_folders', kwargs={
                'username': 'foo',
            }))

    def test_redirects_to_parent(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:delete_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertEqual(response.url, reverse(
            'submissions:view_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderB.id,
                'folder_slug': self.folderB.slug,
            }))


class TestUpdateSubmissionOrderInFolderView(
        SubmissionsFolderViewsBaseTestCase):
    def test_restricts_to_folder_owner(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:update_submission_order_in_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderA.id,
                'folder_slug': self.folderA.slug,
            }))
        self.assertContains(response, "You can't sort a folder that isn't "
                            "yours", status_code=403)

    def test_breadcrumbs(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:update_submission_order_in_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertContains(
            response, ('/<a href="{}"><em>{}</em></a>'
                       '/<em>{}</em>').format(
                           reverse('submissions:view_folder', kwargs={
                               'username': 'foo',
                               'folder_id': self.folderB.id,
                               'folder_slug': self.folderB.slug}),
                           self.folderB.name,
                           self.folderC.name))

    def test_lists_submissions(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:update_submission_order_in_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_saves_submission_order(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse(
            'submissions:update_submission_order_in_folder', kwargs={
                'username': 'foo',
                'folder_id': self.folderC.id,
                'folder_slug': self.folderC.slug,
            }) + '?ids=3&ids=2', follow=True)
        self.assertContains(response, 'Submissions sorted successfully.')
        self.assertEqual(FolderItem.objects.get(id=2).position, 2)
