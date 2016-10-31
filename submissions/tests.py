from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import (
    Folder,
    FolderItem,
    Submission,
)
from social.models import Rating
from usermgmt.group_models import FriendGroup
from usermgmt.models import Profile


class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.foo = User.objects.create_user('foo', 'foo@example.com',
                                           'a good password')
        cls.foo.profile = Profile(profile_raw='Wow!',
                                  display_name='Mx Foo Bar')
        cls.foo.profile.save()
        cls.submission1 = Submission(
            owner=cls.foo,
            title='Submission 1',
            description_raw='Description for submission 1',
            content_raw='Content for submission 1',
        )
        cls.submission1.save()
        cls.folder = Folder(
            owner=cls.foo,
            name='Folder 1')
        cls.folder.save()


class TestSubmissionModel(ModelTest):
    def test_get_average_rating_default(self):
        self.assertEqual(self.submission1.get_average_rating(), {
            'stars': '',
            'average': 0,
            'count': 0,
        })

    def test_get_average_rating_with_ratings(self):
        Rating(
            owner=self.foo,
            submission=self.submission1,
            rating=1).save()
        Rating(
            owner=self.foo,
            submission=self.submission1,
            rating=5).save()
        self.assertEqual(self.submission1.get_average_rating(), {
            u'average': 3.0,
            u'count': 2,
            u'stars': u'&#x2605;&#x2605;&#x2605;&#x2606;&#x2606;'
        })

    def test_str(self):
        self.assertEqual(self.submission1.__str__(),
                         'Submission 1 by ~foo (id:1)')

    def test_unicode(self):
        self.assertEqual(self.submission1.__unicode__(),
                         'Submission 1 by ~foo (id:1)')


class TestFolderModel(ModelTest):
    def test_str(self):
        self.assertEqual(self.folder.__str__(), 'Folder 1')

    def test_unicode(self):
        self.assertEqual(self.folder.__unicode__(), 'Folder 1')


class SubmissionsViewsBaseTestCase(TestCase):
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
        cls.baz = User.objects.create_user('baz', 'baz@example.com',
                                           'wow a good password')
        cls.baz.profile = Profile(profile_raw='Honk', display_name='BAZ Wolf')
        cls.baz.profile.save()
        cls.group = FriendGroup(name='Group 1')
        cls.group.save()
        cls.foo.profile.friend_groups.add(cls.group)
        cls.submission1 = Submission(
            owner=cls.foo,
            title='Submission 1',
            description_raw='Description for submission 1',
            content_raw='Content for submission 1',
        )
        cls.submission1.save()
        cls.submission2 = Submission(
            owner=cls.foo,
            title='Submission 2',
            description_raw='Description for submission 2',
            content_raw='Content for submission 2',
        )
        cls.submission2.save()
        cls.bar.profile.favorited_submissions.add(cls.submission1)
        cls.bar.profile.favorited_submissions.add(cls.submission2)
        cls.bar.profile.save()


class TestLoggedOutListUserSubmissionsView(SubmissionsViewsBaseTestCase):
    def test_all_visible(self):
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_one_marked_hidden(self):
        self.submission2.hidden = True
        self.submission2.save()
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_one_marked_adult(self):
        self.submission2.adult_rating = True
        self.submission2.save()
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_one_restricted_to_groups(self):
        self.submission2.restricted_to_groups = True
        self.submission2.save()
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_paginate_after_25(self):
        for i in range(3, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission {}'.format(i),
                description_raw='Description',
                content_raw='Content',
            )
            submission.save()
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, '<a href="{}">2</a>'.format(
            reverse('submissions:list_user_submissions', kwargs={
                'username': 'foo',
                'page': 2
            })))

    def test_reset_paginate_if_out_of_range(self):
        for i in range(3, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission {}'.format(i),
                description_raw='Description',
                content_raw='Content',
            )
            submission.save()
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={
                'username': 'foo',
                'page': 20,
            }))
        self.assertContains(response,
                            '2 <span class="sr-only">(current)</span>')


class TestLoggedInListUserSubmissionsView(SubmissionsViewsBaseTestCase):
    def test_blocked_user_forbidden(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.foo.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertEqual(response.status_code, 403)

    def test_author_can_view_own_hidden_submissions(self):
        self.submission2.hidden = True
        self.submission2.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_author_can_see_own_adult_submissions(self):
        self.submission2.adult_rating = True
        self.submission2.save()
        self.foo.profile.can_see_adult_submissions = False
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_respect_users_results_per_page(self):
        self.bar.profile.results_per_page = 1
        self.bar.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')
        self.assertContains(response, '<a href="{}">2</a>'.format(
            reverse('submissions:list_user_submissions', kwargs={
                'username': 'foo',
                'page': 2
            })))

    def test_group_locked_submission_without_matching_group_not_shown(self):
        self.submission2.restricted_to_groups = True
        self.submission2.save()
        self.submission2.allowed_groups.add(self.group)
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_group_locked_submission_with_matching_group_shown(self):
        self.group.users.add(self.bar)
        self.group.save()
        self.bar.profile.results_per_page = 25
        self.bar.profile.save()
        self.submission2.restricted_to_groups = True
        self.submission2.hidden = False
        self.submission2.allowed_groups.add(self.group)
        self.submission2.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_author_can_see_own_group_locked_submissions(self):
        self.submission2.restricted_to_groups = True
        self.submission2.save()
        self.submission2.allowed_groups.add(self.group)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={'username': 'foo'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')


class TestLoggedOutListUserFavoritesView(SubmissionsViewsBaseTestCase):
    def test_all_visible(self):
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_one_marked_hidden(self):
        self.submission2.hidden = True
        self.submission2.save()
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_one_marked_adult(self):
        self.submission2.adult_rating = True
        self.submission2.save()
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_one_restricted_to_groups(self):
        self.submission2.restricted_to_groups = True
        self.submission2.save()
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_paginate_after_25(self):
        for i in range(3, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission {}'.format(i),
                description_raw='Description',
                content_raw='Content',
            )
            submission.save()
            self.bar.profile.favorited_submissions.add(submission)
        self.bar.save()
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        print(response.content)
        self.assertContains(response, '<a href="{}">2</a>'.format(
            reverse('submissions:list_user_favorites', kwargs={
                'username': 'bar',
                'page': 2
            })))

    def test_reset_paginate_if_out_of_range(self):
        for i in range(3, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission {}'.format(i),
                description_raw='Description',
                content_raw='Content',
            )
            submission.save()
            self.bar.profile.favorited_submissions.add(submission)
        self.bar.profile.save()
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={
                'username': 'bar',
                'page': 2
            }))
        self.assertContains(response,
                            '2 <span class="sr-only">(current)</span>')


class TestLoggedInListUserFavoritesView(SubmissionsViewsBaseTestCase):
    def test_blocked_user_forbidden(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.foo.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'foo'}))
        self.assertEqual(response.status_code, 403)

    def test_author_can_view_own_hidden_submissions(self):
        self.submission2.hidden = True
        self.submission2.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_author_can_see_own_adult_submissions(self):
        self.submission2.adult_rating = True
        self.submission2.save()
        self.foo.profile.can_see_adult_submissions = False
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_respect_users_results_per_page(self):
        self.bar.profile.results_per_page = 1
        self.bar.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')
        self.assertContains(response, '<a href="{}">2</a>'.format(
            reverse('submissions:list_user_favorites', kwargs={
                'username': 'bar',
                'page': 2
            })))

    def test_group_locked_submission_without_matching_group_not_shown(self):
        self.submission2.restricted_to_groups = True
        self.submission2.save()
        self.submission2.allowed_groups.add(self.group)
        self.client.login(username='baz',
                          password='wow a good password')
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_group_locked_submission_with_matching_group_shown(self):
        self.group.users.add(self.baz)
        self.group.save()
        self.submission2.restricted_to_groups = True
        self.submission2.hidden = False
        self.submission2.allowed_groups.add(self.group)
        self.submission2.save()
        self.client.login(username='baz',
                          password='wow a good password')
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')

    def test_author_can_see_own_group_locked_submissions(self):
        self.submission2.restricted_to_groups = True
        self.submission2.save()
        self.submission2.allowed_groups.add(self.group)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'submissions:list_user_favorites', kwargs={'username': 'bar'}))
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')


class TestLoggedOutViewSubmissionView(SubmissionsViewsBaseTestCase):
    def test_view_submission(self):
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertContains(response, 'Content for submission 1')
        self.assertContains(response, '<dt>Views</dt>')
        self.assertContains(response, '<dd>1</dd>')

    def test_view_submission_redirects_to_complete_url(self):
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={'submission_id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(
            'submissions:view_submission', kwargs={
                'username': 'foo',
                'submission_id': 1,
                'submission_slug': 'submission-1'
            }))

    def test_submission_marked_adult_forbidden(self):
        self.submission1.adult_rating = True
        self.submission1.save()
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_submission_marked_hidden_forbidden(self):
        self.submission1.hidden = True
        self.submission1.save()
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_submission_restricted_to_groups_forbidden(self):
        self.submission1.restricted_to_groups = True
        self.submission1.save()
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)


class TestLoggedInViewSubmissionView(SubmissionsViewsBaseTestCase):
    def test_blocked_user_forbidden(self):
        self.foo.profile.blocked_users.add(self.bar)
        self.foo.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_submission_marked_adult_forbidden(self):
        self.submission1.adult_rating = True
        self.submission1.save()
        self.bar.profile.can_see_adult_submissions = False
        self.bar.profile.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_submission_marked_hidden_forbidden(self):
        self.submission1.hidden = True
        self.submission1.save()
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_author_can_see_own_adult_submission(self):
        self.submission1.adult_rating = True
        self.submission1.save()
        self.foo.profile.can_see_adult_submissions = False
        self.foo.profile.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 200)

    def test_author_can_view_own_hidden_submission(self):
        self.submission1.hidden = True
        self.submission1.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 200)

    def test_group_locked_submission_without_matching_group_not_shown(self):
        self.submission1.restricted_to_groups = True
        self.submission1.save()
        self.submission1.allowed_groups.add(self.group)
        self.client.login(username='baz',
                          password='wow a good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_group_locked_submission_with_matching_group_shown(self):
        self.group.users.add(self.baz)
        self.group.save()
        self.submission1.restricted_to_groups = True
        self.submission1.hidden = False
        self.submission1.allowed_groups.add(self.group)
        self.submission1.save()
        self.client.login(username='baz',
                          password='wow a good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 200)

    def test_author_can_see_own_group_locked_submissions(self):
        self.submission1.restricted_to_groups = True
        self.submission1.save()
        self.submission1.allowed_groups.add(self.group)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 200)


class TestEditSubmissionView(SubmissionsViewsBaseTestCase):
    def test_logged_out_forbidden(self):
        response = self.client.get(reverse('submissions:edit_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 302)

    def test_only_own_submission(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse('submissions:edit_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_form_renders(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('submissions:edit_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertContains(
            response,
            'Update submission</button')

    def test_can_save_form(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(
            reverse('submissions:edit_submission',
                    kwargs={
                        'username': 'foo',
                        'submission_id': 1,
                        'submission_slug': 'submission-1',
                    }),
            {
                'title': 'Wow, a new title!',
                'content_raw': 'A whole new story!',
                'tags': 'foo,bar',
            },
            follow=True)
        self.assertContains(response, 'Wow, a new title!')
        self.assertContains(response, 'A whole new story!')
        self.assertTrue('foo' in [
            tag.name for tag in self.submission1.tags.all()])
        self.assertNotEqual(self.submission1.ctime, self.submission1.mtime)

    def test_can_add_to_folders(self):
        folder = Folder(
            owner=self.foo,
            name='Folder 1')
        folder.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(
            reverse('submissions:edit_submission',
                    kwargs={
                        'username': 'foo',
                        'submission_id': 1,
                        'submission_slug': 'submission-1',
                    }),
            {
                'title': 'Wow, a new title!',
                'content_raw': 'A whole new story!',
                'folders': [folder.id],
                'tags': 'foo,bar',
            },
            follow=True)
        self.assertContains(response, 'Wow, a new title!')
        self.assertContains(response, 'A whole new story!')
        self.assertEqual(folder.submissions.count(), 1)

    def test_can_remove_from_folders(self):
        folder = Folder(
            owner=self.foo,
            name='Folder 1')
        folder.save()
        FolderItem(
            folder=folder,
            submission=self.submission1,
            position=1).save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(
            reverse('submissions:edit_submission',
                    kwargs={
                        'username': 'foo',
                        'submission_id': 1,
                        'submission_slug': 'submission-1',
                    }),
            {
                'title': 'Wow, a new title!',
                'content_raw': 'A whole new story!',
                'folders': [],
                'tags': 'foo,bar',
            },
            follow=True)
        self.assertContains(response, 'Wow, a new title!')
        self.assertContains(response, 'A whole new story!')
        self.assertEqual(folder.submissions.count(), 0)

    def test_can_add_to_groups(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(
            reverse('submissions:edit_submission',
                    kwargs={
                        'username': 'foo',
                        'submission_id': 1,
                        'submission_slug': 'submission-1',
                    }),
            {
                'title': 'Wow, a new title!',
                'content_raw': 'A whole new story!',
                'allowed_groups': [self.group.id],
                'tags': 'foo,bar',
            },
            follow=True)
        self.assertContains(response, 'Wow, a new title!')
        self.assertContains(response, 'A whole new story!')
        self.assertEqual(self.submission1.allowed_groups.count(), 1)

    def test_can_remove_from_groups(self):
        self.submission1.allowed_groups.add(self.group)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(
            reverse('submissions:edit_submission',
                    kwargs={
                        'username': 'foo',
                        'submission_id': 1,
                        'submission_slug': 'submission-1',
                    }),
            {
                'title': 'Wow, a new title!',
                'content_raw': 'A whole new story!',
                'folders': [],
                'tags': 'foo,bar',
            },
            follow=True)
        self.assertContains(response, 'Wow, a new title!')
        self.assertContains(response, 'A whole new story!')
        self.assertEqual(self.submission1.allowed_groups.count(), 0)


class TestDeleteSubmissionView(SubmissionsViewsBaseTestCase):
    def test_logged_out_forbidden(self):
        response = self.client.get(reverse('submissions:delete_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 302)

    def test_only_own_submission(self):
        self.client.login(username='bar',
                          password='another good password')
        response = self.client.get(reverse('submissions:delete_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertEqual(response.status_code, 403)

    def test_ask_for_confirmation(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('submissions:delete_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertContains(response,
                            'Are you sure that you want to do this?')

    def test_delete_on_confirmation(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('submissions:delete_submission',
                                    kwargs={
                                        'username': 'foo',
                                        'submission_id': 1,
                                        'submission_slug': 'submission-1',
                                    }), follow=True)
        self.assertContains(response, 'Mx Foo Bar')
        self.assertEqual(Submission.objects.count(), 1)


class TestSubmitView(SubmissionsViewsBaseTestCase):
    def test_logged_out_forbidden(self):
        response = self.client.get(reverse('submissions:submit'))
        self.assertEqual(response.status_code, 302)

    def test_form_renders(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('submissions:submit'))
        self.assertContains(
            response,
            'Update submission</button>')

    def test_submission_created(self):
        self.folder = Folder(
            owner=self.foo,
            name='Folder 1')
        self.folder.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('submissions:submit'),
                                    {
                                        'title': 'Reasons foxes are great',
                                        'content_raw': 'There are too many.',
                                        'folders': [self.folder.id],
                                        'allowed_groups': [self.group.id],
                                        'tags': 'foo, bar',
                                    }, follow=True)
        self.assertContains(response, 'Reasons foxes are great')
        self.assertContains(response, '<a href="{}">foo</a>'.format(
            reverse('tags:view_tag', kwargs={'tag_slug': 'foo'})))
        self.assertEqual(self.folder.submissions.count(), 1)
        self.assertEqual(self.group.submission_set.count(), 1)
