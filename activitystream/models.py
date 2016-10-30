from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Activity(models.Model):
    ACTIVITY_TYPES = (
        # Users and profiles
        ('user:reg', 'user: registered'),
        ('user:login', 'user: logged in'),
        ('user:logout', 'user: logged out'),
        ('user:pwchange', 'user: password changed'),  # TODO
        ('user:pwreset', 'user: password reset'),  # TODO
        ('profile:update', 'user: profile updated'),
        ('profile:view', 'user: profile viewed'),

        # Administration flags
        ('adminflag:create', 'administration flag: created'),
        ('adminflag:update', 'administration flag: updated'),
        ('adminflag:delete', 'administration flag: deleted'),
        ('adminflag:view', 'administration flag: viewed'),

        # User groups
        ('group:create', 'group: created'),
        ('group:update', 'group: updated'),
        ('group:delete', 'group: deleted'),

        # Social interactions
        ('social:watch', 'social: watch user'),
        ('social:unwatch', 'social: unwatch user'),
        ('social:block', 'social: block user'),
        ('social:unblock', 'social: unblock user'),
        ('social:favorite', 'social: favorite submission'),
        ('social:unfavorite', 'social: unfavorite submission'),
        ('social:rate', 'social: rate submission'),
        ('social:enjoy', 'social: enjoy submission'),

        # Submissions
        ('submission:create', 'submission: created'),
        ('submission:update', 'submission: updated'),
        ('submission:delete', 'submission: deleted'),
        ('submission:view', 'submission: viewed'),

        # Submission folders
        ('folder:create', 'folder: created'),
        ('folder:update', 'folder: updated'),
        ('folder:delete', 'folder: deleted'),
        ('folder:view', 'folder: viewed'),
        ('folder:sort', 'folder: sorted'),

        # Tags
        ('tag:create', 'tag: tag created'),
        ('tag:tag', 'tag: tagged item created'),

        # Comments
        ('comment:create', 'comment: created'),
        ('comment:update', 'comment: updated'),
        ('comment:delete', 'comment: deleted'),

        # Promotions
        ('promotion:create', 'promotion: created'),
        ('promotion:retire', 'promotion: retired'),
        ('ad:create', 'ad: created,'),
        ('ad:update', 'ad: update'),
        ('ad:golive', 'ad: went live'),
        ('ad:retire', 'ad: retired'),

        # Publisher pages
        ('publisher:create', 'publisher: created'),
        ('publisher:update', 'publisher: updated'),
        ('publisher:delete', 'publisher: deleted'),
        ('publisher:view', 'publisher: viewed'),
        ('publisher:claimed', 'publisher: claimed'),

        # Search
        ('search:search', 'search: run'),
    )

    activity_time = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object_model = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, app, action, object_model):
        item_type = "{}:{}".format(app.lower(), action.lower())
        if item_type not in dict(Activity.ACTIVITY_TYPES):
            return  # XXX should we fail silently?
        activity = cls(activity_type=item_type)
        activity.object_model = object_model
        activity.save()

    class Meta:
        ordering = ['-activity_time']
