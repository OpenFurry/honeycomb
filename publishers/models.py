from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from administration.models import Flag


class PublisherPage(models.Model):
    """A page on the site representing a publisher, collecting submissions by
    site members who are employed by or contracted under that publisher.
    """
    # The name and slug of the page
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    # The publisher's URL
    url = models.URLField(max_length=1024)

    # The page content
    body = models.TextField()

    # The page owner
    owner = models.ForeignKey(User, related_name='owned_publisher_page')

    # Users who have been published by the publisher
    members = models.ManyToManyField(User)

    flags = GenericRelation(Flag)
