from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from taggit.models import Tag

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
            ctime=timezone.now(),
            owner=cls.foo,
            title='Submission 1',
            content_raw='Whoa, a submission')
        cls.submission1.save(update_content=True)
        cls.submission2 = Submission(
            ctime=timezone.now(),
            owner=cls.foo,
            title='Submission 2',
            content_raw='Whoa, another submission')
        cls.submission2.save(update_content=True)
        cls.test_tag = Tag(name='test')
        cls.test_tag.save()


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
                'font-size:calc(14px * 3.0);'))
        self.assertContains(
            response, '<a href="{}" style="{}">green</a>'.format(
                reverse('tags:view_tag', kwargs={'tag_slug': 'green'}),
                'font-size:calc(14px * 3.0);'))
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
                ctime=timezone.now(),
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
                ctime=timezone.now(),
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

    def test_respects_users_requests_per_page(self):
        for i in range(1, 30):
            submission = Submission(
                ctime=timezone.now(),
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


class TestFavoriteTagView(BaseTagViewsTestCase):
    def test_cant_favorite_if_already_favorited(self):
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:favorite_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, 'You have already favorited that tag')

    def test_favorite_tag(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:favorite_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, 'Tag favorited;')
        self.assertEqual(self.foo.profile.favorite_tags.count(), 1)


class TestUnfavoriteTagView(BaseTagViewsTestCase):
    def test_cant_unfavorite_if_not_favorited(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:unfavorite_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, "You haven't favorited that tag")

    def test_unfavorite_tag(self):
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:unfavorite_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, 'Tag unfavorited;')
        self.assertEqual(self.foo.profile.favorite_tags.count(), 0)


class TestListSubmissionsWithFavoriteTagsView(BaseTagViewsTestCase):
    def test_must_favorite_tags(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'tags:list_submissions_with_favorite_tags'), follow=True)
        self.assertContains(response, 'You must favorite some tags')

    def test_lists_favorite_tags(self):
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'tags:list_submissions_with_favorite_tags'))
        self.assertContains(
            response, '<a href="{}" style="{}">test</a>'.format(
                reverse('tags:view_tag', kwargs={'tag_slug': 'test'}),
                'font-size:calc(7px * 5.0);'))

    def test_lists_submissions_with_favorite_tags(self):
        self.submission1.tags.add('test')
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'tags:list_submissions_with_favorite_tags'))
        self.assertContains(response, 'Submission 1')

    def test_paginates_submissions(self):
        for i in range(1, 30):
            submission = Submission(
                ctime=timezone.now(),
                owner=self.foo,
                title='Submission #{}'.format(i),
                content_raw='Submission #{}'.format(i))
            submission.save(update_content=True)
            submission.tags.add('test')
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'tags:list_submissions_with_favorite_tags'))
        self.assertContains(response, 'Showing results 1 through 25 of 29')
        self.assertContains(response, '1 <span class="sr-only">(current)')
        self.assertContains(response, '2/">2</a>')

    def test_defaults_to_last_page(self):
        for i in range(1, 30):
            submission = Submission(
                ctime=timezone.now(),
                owner=self.foo,
                title='Submission #{}'.format(i),
                content_raw='Submission #{}'.format(i))
            submission.save(update_content=True)
            submission.tags.add('test')
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'tags:list_submissions_with_favorite_tags', kwargs={
                'page': 50,
            }))
        self.assertContains(response, 'Showing results 26 through 29 of 29')
        self.assertContains(response, '2 <span class="sr-only">(current)')
        self.assertContains(response, '1/">1</a>')

    def test_respects_users_requests_per_page(self):
        for i in range(1, 30):
            submission = Submission(
                ctime=timezone.now(),
                owner=self.foo,
                title='Submission #{}'.format(i),
                content_raw='Submission #{}'.format(i))
            submission.save(update_content=True)
            submission.tags.add('test')
        self.foo.profile.results_per_page = 10
        self.foo.profile.save()
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.get(reverse(
            'tags:list_submissions_with_favorite_tags'))
        self.assertContains(response, 'Showing results 1 through 10 of 29')
        self.assertContains(response, '1 <span class="sr-only">(current)')
        self.assertContains(response, '2/">2</a>')
        self.assertContains(response, '3/">3</a>')


class TestBlockTagView(BaseTagViewsTestCase):
    def test_cant_block_if_already_blocked(self):
        self.foo.profile.blocked_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:block_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, 'You have already blocked that tag')

    def test_cant_block_if_favorited(self):
        self.foo.profile.favorite_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:block_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, 'unfavorite it first before blocking')

    def test_block_tag(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:block_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, 'Tag blocked.')
        self.assertEqual(self.foo.profile.blocked_tags.count(), 1)


class TestUnblockTagView(BaseTagViewsTestCase):
    def test_cant_unblock_if_not_blocked(self):
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:unblock_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, "You haven't blocked that tag")

    def test_unblock_tag(self):
        self.foo.profile.blocked_tags.add(self.test_tag)
        self.client.login(username='foo',
                          password='a good password')
        response = self.client.post(reverse('tags:unblock_tag', kwargs={
            'tag_slug': self.test_tag.slug,
        }), follow=True)
        self.assertContains(response, 'Tag unblocked.')
        self.assertEqual(self.foo.profile.blocked_tags.count(), 0)
