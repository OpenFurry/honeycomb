from __future__ import unicode_literals
import markdown
from PIL import Image
import pypandoc
import tempfile

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags
from taggit.managers import TaggableManager

from honeycomb_markdown import HoneycombMarkdown
from usermgmt.group_models import FriendGroup


def content_path(instance, filename):
    """Generates a path for a submission's content file.

    Args:
        instance: the instance of :model:`submissions.Submission` to which the
            file belongs
        filename: the original name of the file (ignored)

    Returns:
        The generated path
    """
    return 'uploads/user-{}/content-files/{}'.format(
        instance.owner.id,
        '{}-{}.{}'.format(
            instance.ctime.strftime('%Y-%m-%d-%H%M%S'),
            slugify(instance.title),
            filename.split('.')[-1]))


def icon_path(instance, filename):
    """Generates a path for a submission's icon file.

    Args:
        instance: the instance of :model:`submissions.Submission` to which the
            file belongs
        filename: the original name of the file (ignored)

    Returns:
        The generated path
    """
    return 'uploads/user-{}/icons/{}'.format(
        instance.owner.id,
        '{}-{}.{}'.format(
            instance.ctime.strftime('%Y-%m-%d-%H%M%S'),
            slugify(instance.title),
            filename.split('.')[-1]))


def cover_path(instance, filename):
    """Generates a path for a submission's cover file.

    Args:
        instance: the instance of :model:`submissions.Submission` to which the
            file belongs
        filename: the original name of the file (ignored)

    Returns:
        The generated path
    """
    return 'uploads/user-{}/covers/{}'.format(
        instance.owner.id,
        '{}-{}.{}'.format(
            instance.ctime.strftime('%Y-%m-%d-%H%M%S'),
            slugify(instance.title),
            filename.split('.')[-1]))


class Submission(models.Model):
    """A submission created on the site."""
    # Submission owner
    owner = models.ForeignKey(User)

    # Title and slug generated from title
    title = models.CharField(max_length=1000)
    slug = models.SlugField()

    # Content written by the user
    description_raw = models.TextField(blank=True, verbose_name="description")
    description_rendered = models.TextField(blank=True)
    content_raw = models.TextField(blank=True, verbose_name="submission")
    content_rendered = models.TextField()
    content_file = models.FileField(blank=True, upload_to=content_path)

    # Associated images
    icon = models.ImageField(blank=True, upload_to=icon_path)
    cover = models.ImageField(blank=True, upload_to=cover_path)
    cover_attribution = models.CharField(max_length=1000, blank=True)

    # Flags
    can_comment = models.BooleanField(
        default=True,
        verbose_name='allow comments')
    can_enjoy = models.BooleanField(
        default=True,
        verbose_name='allow enjoy votes')
    adult_rating = models.BooleanField(
        default=False,
        verbose_name='submission for adults only')
    hidden = models.BooleanField(default=False)
    allowed_groups = models.ManyToManyField(FriendGroup, blank=True)

    # Organization
    restricted_to_groups = models.BooleanField(
        default=False,
        verbose_name='restrict visibility to certain groups')
    folders = models.ManyToManyField('Folder', through='FolderItem',
                                     blank=True)

    # Additional metadata
    ctime = models.DateTimeField()  # auto_now_add won't work here [0]
    mtime = models.DateTimeField(blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    enjoy_votes = models.PositiveIntegerField(default=0)
    rating_stars = models.CharField(max_length=40, default='&#x2606;' * 5)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2,
                                         default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        """Overridden save method.

        If instructed through `update_content=True`, this method updates the
        slug, renders the content from the description and submission from
        markdown to HTML, and munges files (resizing images, converting content
        files).
        """
        update_content = (kwargs.pop('update_content')
                          if 'update_content' in kwargs else False)
        if update_content:
            # Set the slug
            self.slug = slugify(self.title)

            # Render description
            self.description_rendered = markdown.markdown(
                strip_tags(self.description_raw),
                extensions=[
                    'pymdownx.extra',
                    'markdown.extensions.codehilite',
                    'pymdownx.headeranchor',
                    'pymdownx.magiclink',
                    'pymdownx.smartsymbols',
                    'pymdownx.tilde',
                    'pymdownx.mark',
                    HoneycombMarkdown(),
                ])

            # Update content from file
            if self.content_file.name:
                with tempfile.NamedTemporaryFile(suffix='.{}'.format(
                        self.content_file.name.split('.')[-1])) as temp:
                    for chunk in self.content_file.chunks():
                        temp.write(chunk)
                    temp.flush()
                    self.content_raw = pypandoc.convert_file(
                        temp.name, 'md')

            # Render content
            self.content_rendered = markdown.markdown(
                strip_tags(self.content_raw),
                extensions=[
                    'pymdownx.extra',
                    'markdown.extensions.codehilite',
                    'pymdownx.headeranchor',
                    'pymdownx.magiclink',
                    'pymdownx.smartsymbols',
                    'pymdownx.tilde',
                    'pymdownx.mark',
                    HoneycombMarkdown(),
                ])

        # Save separately so that self.icon/self.cover are populated below
        super(Submission, self).save(*args, **kwargs)

        if update_content:
            # Resize icon
            if self.icon:
                icon = Image.open(self.icon)
                icon.thumbnail((100, 100), Image.ANTIALIAS)
                icon.save(self.icon.path)

            # Resize cover
            if self.cover:
                cover = Image.open(self.cover)
                cover.thumbnail((2048, 2048), Image.ANTIALIAS)
                cover.save(self.cover.path)

    def get_average_rating(self):
        """Gets the average rating of the submission based on all ratings."""
        total = count = 0
        for rating in self.rating_set.all():
            total += rating.rating
            count += 1
        if count > 0:
            return {
                'stars': '&#x2605;' * int(total / count) +
                         '&#x2606;' * (5 - int(total / count)),
                'average': float(total) / float(count),
                'count': count
            }
        else:
            return {'stars': '', 'average': 0, 'count': 0}

    def get_absolute_url(self):
        """Gets the absolute URL of the image, reversed from patterns."""
        return reverse('submissions:view_submission', kwargs={
            'username': self.owner.username,
            'submission_id': self.id,
            'submission_slug': self.slug,
        })

    def __str__(self):
        return '{} by ~{} (id:{})'.format(self.title, self.owner.username,
                                          self.id)

    def __unicode__(self):
        return '{} by ~{} (id:{})'.format(self.title, self.owner.username,
                                          self.id)


class Folder(models.Model):
    """A folder for storing submissions."""
    # Folder owner
    owner = models.ForeignKey(User)

    # Parent folder
    parent = models.ForeignKey('Folder', blank=True, null=True)

    # Folder name and slug generated from name
    name = models.CharField(max_length=1000)
    slug = models.SlugField()

    # Folder details
    description_raw = models.TextField(blank=True)
    description_rendered = models.TextField(blank=True)
    is_serial = models.BooleanField(default=False)

    submissions = models.ManyToManyField(Submission, through='FolderItem')

    def save(self, *args, **kwargs):
        """Overridden save method for generating folder slugs."""
        self.slug = slugify(self.name)
        super(Folder, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class FolderItem(models.Model):
    """A join item between submission and folder that stores the submission's
    position in the folder.
    """
    # Submission and folder relations
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

    # Position in ordering
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']


# [0] - auto_now_add only sets ctime on save, and various implementations will
# not have that during file path saving.  This must be set by
# submissions:submit, *including in tests*.
