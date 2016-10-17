import unittest

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Submission
from usermgmt.models import Profile


groups_implemented = False


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
        response = self.client.get(reverse(
            'submissions:list_user_submissions', kwargs={
                'username': 'foo',
                'page': 2
            }))
        self.assertContains(response,
                            '1 <span class="sr-only">(current)</span>')


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

    @unittest.skipUnless(groups_implemented, 'requires groups implemented')
    def test_group_locked_submission_without_matching_group_not_shown(self):
        pass

    @unittest.skipUnless(groups_implemented, 'requires groups implemented')
    def test_group_locked_submission_with_matching_group_shown(self):
        pass

    @unittest.skipUnless(groups_implemented, 'requires groups implemented')
    def test_author_can_see_own_group_locked_submissions(self):
        pass


class TestLoggedOutViewSubmissionView(SubmissionsViewsBaseTestCase):
    def test_view_submission(self):
        response = self.client.get(reverse('submissions:view_submission',
                                   kwargs={
                                       'username': 'foo',
                                       'submission_id': 1,
                                       'submission_slug': 'submission-1',
                                   }))
        self.assertContains(response, 'Content for submission 1')
        self.assertContains(response, 'Views: 1')

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

    @unittest.skipUnless(groups_implemented, 'requires groups implemented')
    def test_submission_restricted_to_groups_forbidden(self):
        pass

    @unittest.skipUnless(groups_implemented, 'requires groups implemented')
    def test_author_can_see_own_group_locked_submission(self):
        pass


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
            '<input type="submit" value="Update submission" />')

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
            },
            follow=True)
        self.assertContains(response, 'Wow, a new title!')
        self.assertContains(response, 'A whole new story!')


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
            '<input type="submit" value="Update submission" />')

    def test_submission_created(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('submissions:submit'),
                                    {
                                        'title': 'Reasons foxes are great',
                                        'content_raw': 'There are too many.',
                                    }, follow=True)
        self.assertContains(response, 'Reasons foxes are great')
