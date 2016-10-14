from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Submission(models.Model):
    # Submission owner
    owner = models.ForeignKey(User)

    # Title and slug generated from ID and title
    title = models.CharField(max_length=1000)
    slug = models.SlugField()

    # Content written by the user
    description_raw = models.TextField(blank=True)
    description_rendered = models.TextField(blank=True)
    content_raw = models.TextField(blank=True)
    content_rendered = models.TextField()
    content_file = models.FileField(blank=True)

    # Associated images
    icon = models.ImageField(blank=True)
    cover = models.ImageField(blank=True)

    # Flags
    can_comment = models.BooleanField(default=True)
    can_enjoy = models.BooleanField(default=True)
    hidden = models.BooleanField(default=False)

    # Additional metadata
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)


class Folder(models.Model):
    # Folder owner
    owner = models.ForeignKey(User)

    # Folder name and slug generated from name
    name = models.CharField(max_length=1000)
    slug = models.SlugField()


class FolderItem(models.Model):
    # Submission and folder relations
    submission = models.ForeignKey(Submission)
    folder = models.ForeignKey(Folder)

    # Position in ordering
    position = models.PositiveIntegerField()
