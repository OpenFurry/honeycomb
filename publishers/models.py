from __future__ import unicode_literals
import markdown
from PIL import Image

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags
from submitify.models import Call

from administration.models import Flag
from honeycomb_markdown import HoneycombMarkdown


def _upload_path(instance, filename, upload_type):
    return 'uploads/publisher-{}/{}'.format(
        instance.slug.id,
        '{}-{}.{}'.format(
            timezone.now().strftime('%Y-%m-%d-%H%M%S'),
            upload_type,
            filename.split('.')[-1]))


def logo_path(instance, filename):
    return _upload_path(instance, filename, 'logo')


def banner_path(instance, filename):
    return _upload_path(instance, filename, 'banner')


def newsitem_path(instance, filename):
    return _upload_path(instance.publisher, filename, 'newsitem')


class Publisher(models.Model):
    """A page on the site representing a publisher, collecting submissions by
    site members who are employed by or contracted under that publisher.
    """
    # The name and slug of the page
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    # The publisher's URL
    url = models.URLField(max_length=1024)

    # The page content
    logo = models.ImageField(upload_to=logo_path)
    banner = models.ImageField(blank=True, upload_to=banner_path)
    body_raw = models.TextField(verbose_name='body')
    body_rendered = models.TextField()

    # The page owner
    owner = models.ForeignKey(User, blank=True, null=True,
                              related_name='owned_publisher_page')

    # Users who have an editorial role with the publisher
    editors = models.ManyToManyField(User, related_name='publisher_editor_of')

    # Users who have been published by the publisher
    members = models.ManyToManyField(User, related_name='publisher_member_of')

    # Any calls for submissions run by the publisher
    calls = models.ManyToManyField(Call)

    flags = GenericRelation(Flag)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.body_rendered = markdown.markdown(
            strip_tags(self.body_raw),
            extensions=[
                HoneycombMarkdown(),
                'pymdownx.extra',
                'markdown.extensions.codehilite',
                'pymdownx.headeranchor',
                'pymdownx.magiclink',
                'pymdownx.smartsymbols',
                'pymdownx.tilde',
                'pymdownx.mark',
            ])

        super(Publisher, self).save(*args, **kwargs)

        # Resize images
        if self.logo:
            logo = Image.open(self.logo)
            logo.thumbnail((2048, 2048), Image.ANTIALIAS)
            logo.save(self.logo.path)
        if self.banner:
            banner = Image.open(self.banner)
            banner.thumbnail((2048, 2048), Image.ANTIALIAS)
            banner.save(self.banner.path)

    def get_absolute_url(self):
        return reverse('publishers:view_publisher', kwargs={
            'slug': self.slug,
        })


class NewsItem(models.Model):
    """An item of news from the publisher on their page."""
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    owner = models.ForeignKey(User)
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    image = models.ImageField(blank=True, upload_to=newsitem_path)
    subject = models.CharField(max_length=200)
    body_raw = models.TextField(verbose_name='body')
    body_rendered = models.TextField()

    def save(self, *args, **kwargs):
        self.body_rendered = markdown.markdown(
            strip_tags(self.body_raw),
            extensions=[
                HoneycombMarkdown(),
                'pymdownx.extra',
                'markdown.extensions.codehilite',
                'pymdownx.headeranchor',
                'pymdownx.magiclink',
                'pymdownx.smartsymbols',
                'pymdownx.tilde',
                'pymdownx.mark',
            ])

        super(NewsItem, self).save(*args, **kwargs)

        if self.image:
            image = Image.open(self.image)
            image.thumbnail((2048, 2048), Image.ANTIALIAS)
            image.save(self.image.path)

    def get_absolute_url(self):
        return reverse('publishers:view_news_item', kwargs={
            'publisher_slug': self.publisher.slug,
            'item_id': self.id,
        })
