from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from submissions.models import Submission
from usermgmt.models import Profile


class BaseTagViewsTestCase(TestCase):
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
            content_raw='Whoa, a submission')
        cls.submission1.save(update_content=True)
        cls.submission2 = Submission(
            owner=cls.foo,
            title='Submission 2',
            content_raw='Whoa, another submission')
        cls.submission2.save(update_content=True)


class TestListTagsView(BaseTagViewsTestCase):
    def test_renders_empty_tag_cloud(self):
        response = self.client.get(reverse('tags:list_tags'))
        self.assertContains(response, 'Submission tags')

    def test_renders_full_tag_cloud(self):
        self.submission1.tags.add('red', 'green', 'blue')
        self.submission2.tags.add('red')
        response = self.client.get(reverse('tags:list_tags'))
        self.assertContains(
            response, '<a href="{}" style="{}">blue</a>'.format(
                reverse('tags:view_tag', kwargs={'tag_slug': 'blue'}),
                'font-size:calc(14px * 1.0);'))
        self.assertContains(
            response, '<a href="{}" style="{}">green</a>'.format(
                reverse('tags:view_tag', kwargs={'tag_slug': 'green'}),
                'font-size:calc(14px * 1.0);'))
        self.assertContains(
            response, '<a href="{}" style="{}">red</a>'.format(
                reverse('tags:view_tag', kwargs={'tag_slug': 'red'}),
                'font-size:calc(14px * 5.0);'))


class TestViewTagView(BaseTagViewsTestCase):
    def test_lists_tagged_submissions(self):
        self.submission1.tags.add('red', 'green', 'blue')
        self.submission2.tags.add('red')
        response = self.client.get(reverse('tags:view_tag', kwargs={
            'tag_slug': 'red'
        }))
        self.assertContains(response, 'Submissions tagged "red"')
        self.assertContains(response, 'Submission 1')
        self.assertContains(response, 'Submission 2')
        response = self.client.get(reverse('tags:view_tag', kwargs={
            'tag_slug': 'green'
        }))
        self.assertContains(response, 'Submissions tagged "green"')
        self.assertContains(response, 'Submission 1')
        self.assertNotContains(response, 'Submission 2')

    def test_paginates_submissions(self):
        for i in range(1, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission #{}'.format(i),
                content_raw='Submission #{}'.format(i))
            submission.save(update_content=True)
            submission.tags.add('red')
        response = self.client.get(reverse('tags:view_tag', kwargs={
            'tag_slug': 'red'
        }))
        self.assertContains(response, 'Submissions tagged "red"')
        self.assertContains(response, 'Showing results 1 through 25 of 29')
        self.assertContains(response, '1 <span class="sr-only">(current)')
        self.assertContains(response, '2/">2</a>')

    def test_defaults_to_last_page(self):
        for i in range(1, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission #{}'.format(i),
                content_raw='Submission #{}'.format(i))
            submission.save(update_content=True)
            submission.tags.add('red')
        response = self.client.get(reverse('tags:view_tag', kwargs={
            'tag_slug': 'red',
            'page': 50,
        }))
        self.assertContains(response, 'Submissions tagged "red"')
        self.assertContains(response, 'Showing results 26 through 29 of 29')
        self.assertContains(response, '2 <span class="sr-only">(current)')
        self.assertContains(response, '1/">1</a>')

    def test_resects_users_requests_per_page(self):
        for i in range(1, 30):
            submission = Submission(
                owner=self.foo,
                title='Submission #{}'.format(i),
                content_raw='Submission #{}'.format(i))
            submission.save(update_content=True)
            submission.tags.add('red')
        self.foo.profile.results_per_page = 10
        self.foo.profile.save()
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse('tags:view_tag', kwargs={
            'tag_slug': 'red'
        }))
        self.assertContains(response, 'Submissions tagged "red"')
        self.assertContains(response, 'Showing results 1 through 10 of 29')
        self.assertContains(response, '1 <span class="sr-only">(current)')
        self.assertContains(response, '2/">2</a>')
        self.assertContains(response, '3/">3</a>')
