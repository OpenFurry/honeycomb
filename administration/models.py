from __future__ import unicode_literals
import hashlib
import markdown

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from honeycomb_markdown import HoneycombMarkdown


class Application(models.Model):
    PUBLISHER = 'p'
    CLAIM_PUBLISHER = 'c'
    EVENT = 'e'
    AD = 'a'
    AD_LIFECYCLE = 'l'
    CONTENT_MODERATOR = 'm'
    SOCIAL_MODERATOR = 's'
    # TODO third item in tuple should be next_url for taking the necessary
    # action.
    # @makyo 2016-11-07 #66
    APPLICATION_TYPES = (
        (PUBLISHER, 'Create a publisher page'),
        (CLAIM_PUBLISHER, 'Claim a publisher'),
        (EVENT, 'Schedule an event'),
        (AD, 'Create an ad'),
        (AD_LIFECYCLE, 'Schedule an ad lifecycle'),
        (SOCIAL_MODERATOR, 'Become a social moderator'),
        (CONTENT_MODERATOR, 'Become a content moderator'),
    )
    SOCIAL_TYPES = (
        CLAIM_PUBLISHER,
        CONTENT_MODERATOR,
        SOCIAL_MODERATOR,
    )
    CONTENT_TYPES = (
        PUBLISHER,
        EVENT,
        AD,
        AD_LIFECYCLE,
    )

    ACCEPTED = 'a'
    REJECTED = 'r'
    RESOLUTION_TYPES = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )

    applicant = models.ForeignKey(User, related_name='applications')
    admin_contact = models.ForeignKey(
        User, null=True, related_name='applications_responsible_for')

    ctime = models.DateTimeField(auto_now_add=True)
    application_type = models.CharField(max_length=1,
                                        choices=APPLICATION_TYPES)
    body_raw = models.TextField(verbose_name='body')
    body_rendered = models.TextField()
    resolution = models.CharField(max_length=1, blank=True,
                                  choices=RESOLUTION_TYPES)

    def get_absolute_url(self):
        return reverse('administration:view_application', kwargs={
            'application_id': self.id
        })

    def save(self, *args, **kwargs):
        self.body_rendered = markdown.markdown(
            self.body_raw,
            extensions=[
                'pymdownx.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.smarty',
                'pymdownx.headeranchor',
                'pymdownx.magiclink',
                'pymdownx.smartsymbols',
                'pymdownx.tilde',
                'pymdownx.mark',
                HoneycombMarkdown(),
            ])
        super(Application, self).save(*args, **kwargs)

    class Meta:
        ordering = ('resolution', '-ctime')
        permissions = (
            ('can_list_social_applications', 'Can list social applications'),
            ('can_view_social_applications', 'Can view social applications'),
            ('can_resolve_social_applications',
             'Can resolve social applications'),
            ('can_list_content_applications',
             'Can list content applications'),
            ('can_view_content_applications',
             'Can view content applications'),
            ('can_resolve_content_applications',
             'Can resolve content applications'),
            ('can_resolve_applications', 'Can resolve applications'),
        )


class Flag(models.Model):
    """Represents an item flagged for administrative attention."""
    SOCIAL = 's'
    CONTENT = 'c'
    FLAG_TYPES = (
        (SOCIAL, 'Social'),
        (CONTENT, 'Content'),
    )

    # The object being flagged
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object_model = GenericForeignKey('content_type', 'object_id')
    flagged_object_owner = models.ForeignKey(User, blank=True, null=True,
                                             related_name="flagged_objects")

    # All participants able to take part in a discussion over a flag
    participants = models.ManyToManyField(User, blank=True,
                                          related_name="flags_party_to")

    # The user who flagged the object
    flagged_by = models.ForeignKey(User)

    # Flag information
    flag_type = models.CharField(
        max_length=1, choices=FLAG_TYPES, help_text="""Pick 'content' if the
        issue is with the content of the object, such as a violation of the
        acceptable upload policy.  Pick 'social' if the issue is with the way
        the creator of the content is behaving, such as a violation of the
        terms of service.""")
    ctime = models.DateTimeField(auto_now_add=True)
    resolved = models.DateTimeField(null=True)
    resolved_by = models.ForeignKey(User, related_name='resolved_flags',
                                    null=True)
    resolution = models.TextField(blank=True)
    subject = models.CharField(max_length=100, help_text="""Briefly describe
    the issue with the content or user. (100 characters)""")
    body_raw = models.TextField(verbose_name='body', help_text="""Describe
    the issue with the content or the user.  Be as specific as possible,
    including as many details and as much evidence as you can.  Markdown is
    allowed.""")
    body_rendered = models.TextField()

    def get_absolute_url(self):
        return reverse('administration:view_flag', kwargs={
            'flag_id': self.id,
        })

    def save(self, *args, **kwargs):
        self.body_rendered = markdown.markdown(
            self.body_raw,
            extensions=[
                'pymdownx.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.smarty',
                'pymdownx.headeranchor',
                'pymdownx.magiclink',
                'pymdownx.smartsymbols',
                'pymdownx.tilde',
                'pymdownx.mark',
                HoneycombMarkdown(),
            ])
        super(Flag, self).save(*args, **kwargs)

    def __str__(self):
        return '{} (against {})'.format(self.subject, str(self.object_model))

    def __unicode__(self):
        return '{} (against {})'.format(self.subject, str(self.object_model))

    class Meta:
        ordering = ['-ctime']
        permissions = (
            ('can_list_social_flags', 'Can list social flags'),
            ('can_view_social_flags', 'Can view social flags'),
            ('can_resolve_social_flags', 'Can resolve social flags'),
            ('can_list_content_flags', 'Can list content flags'),
            ('can_view_content_flags', 'Can view content flags'),
            ('can_resolve_content_flags', 'Can resolve content flags'),
            ('can_resolve_flags', 'Can resolve flags'),
        )


class Ban(models.Model):
    """Represents a temporary or permanent ban on a user."""
    # The user being banned
    user = models.ForeignKey(User)

    # The admin who banned the user
    admin_contact = models.ForeignKey(User, related_name='banned_users')

    # The time period of the ban
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    user_has_viewed = models.BooleanField(default=False)

    # The reason for the ban
    reason_raw = models.TextField(verbose_name='reason')
    reason_rendered = models.TextField()

    # Any administrative flags if applicable
    flags = models.ManyToManyField(Flag, blank=True,
                                   verbose_name='Pertinent flags')

    def get_absolute_url(self):
        return reverse('administration:view_ban', kwargs={
            'ban_id': self.id,
        })

    def get_ban_hash(self):
        hashtext = '{}:{}'.format(self.id, self.reason_raw)
        return hashlib.sha1(hashtext.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        self.reason_rendered = markdown.markdown(
            self.reason_raw,
            extensions=[
                'pymdownx.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.smarty',
                'pymdownx.headeranchor',
                'pymdownx.magiclink',
                'pymdownx.smartsymbols',
                'pymdownx.tilde',
                'pymdownx.mark',
                HoneycombMarkdown(),
            ])
        super(Ban, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-start_date',)
        permissions = (
            ('can_ban_users', 'Can ban users'),
            ('can_list_bans', 'Can list bans'),
            ('can_view_bans', 'Can view bans'),
            ('can_lift_bans', 'Can lift bans'),
        )
