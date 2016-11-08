from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Activity(models.Model):
    """Represents a single activity item in the stream of site activity."""
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
        ('adminapplication:create', 'administration application: created'),
        ('adminapplication:update', 'administration application: updated'),
        ('adminapplication:delete', 'administration application: deleted'),
        ('adminapplication:view', 'administration application: viewed'),
        ('adminban:create', 'administration ban: created'),
        ('adminban:update', 'administration ban: updated'),
        ('adminban:delete', 'administration ban: deleted'),
        ('adminban:view', 'administration ban: viewed'),

        # User groups
        ('group:create', 'group: created'),
        ('group:update', 'group: updated'),
        ('group:delete', 'group: deleted'),

        # Social interactions
        ('social:watch', 'social: watch user'),
        ('social:unwatch', 'social: unwatch user'),
        ('social:block', 'social: block user'),
        ('social:unblock', 'social: unblock user'),
        ('social:message', 'social: message user'),
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
        ('search:basic_search', 'search: basic search run'),
    )

    activity_time = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object_model = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, app, action, object_model):
        """Creates a new activity stream item in a simple fashion.

        This classmethod attempts to create an activity by building the
        activity_type from the app and action args.  If such an action doesn't
        exist, it fails silently, to allow adding or removing actions to be
        painless.

        Args:
            app: the application, model, or category portion of the
                activity_type
            action: the action portion of the activity type
            object_model: an object for the activity to refer to, such as a
            :model:`submissions.Submission`

        Returns:
            The generated :model:`activitystream.Activity`
        """
        item_type = "{}:{}".format(app.lower(), action.lower())
        if item_type not in dict(Activity.ACTIVITY_TYPES):
            return None
        activity = cls(activity_type=item_type)
        activity.object_model = object_model
        activity.save()
        return activity

    class Meta:
        ordering = ['-activity_time']
