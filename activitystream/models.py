from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Activity(models.Model):
    ACTIVITY_TYPES = (
        # Users and profiles
        ('USER:REG', 'User: registered'),
        ('USER:LOGIN', 'User: logged in'),
        ('USER:LOGOUT', 'User: logged out'),
        ('USER:PWCHANGE', 'User: password changed'),
        ('USER:PWRESET', 'User: password reset'),
        ('PROFILE:UPDATE', 'User: profile updated'),
        ('PROFILE:VIEW', 'User: profile viewed'),

        # Administration flags
        ('ADMINFLAG:CREATE', 'Administration flag: created'),
        ('ADMINFLAG:UPDATE', 'Administration flag: updated'),
        ('ADMINFLAG:DELETE', 'Administration flag: deleted'),
        ('ADMINFLAG:VIEW', 'Administration flag: viewed'),

        # User groups
        ('GROUP:CREATE', 'Group: created'),
        ('GROUP:UPDATE', 'Group: updated'),
        ('GROUP:DELETE', 'Group: deleted'),
        ('GROUP:VIEW', 'Group: viewed'),

        # Social interactions
        ('SOCIAL:WATCH', 'Social: watch user'),
        ('SOCIAL:UNWATCH', 'Social: unwatch user'),
        ('SOCIAL:BLOCK', 'Social: block user'),
        ('SOCIAL:UNBLOCK', 'Social: unblock user'),
        ('SOCIAL:FAVORITE', 'Social: favorite submission'),
        ('SOCIAL:UNFAVORITE', 'Social: unfavorite submission'),
        ('SOCIAL:RATE', 'Social: rate submission'),
        ('SOCIAL:ENJOY', 'Social: enjoy submission'),

        # Submissions
        ('SUBMISSION:CREATE', 'Submission: created'),
        ('SUBMISSION:UPDATE', 'Submission: updated'),
        ('SUBMISSION:DELETE', 'Submission: deleted'),
        ('SUBMISSION:VIEW', 'Submission: viewed'),

        # Submission folders
        ('FOLDER:CREATE', 'Folder: created'),
        ('FOLDER:UPDATE', 'Folder: updated'),
        ('FOLDER:DELETE', 'Folder: deleted'),
        ('FOLDER:VIEW', 'Folder: viewed'),
        ('FOLDER:SORT', 'Folder: sorted'),

        # Tags
        ('TAG:CREATE', 'Tag: tag created'),
        ('TAG:TAG', 'Tag: tagged item created'),

        # Comments
        ('COMMENT:CREATE', 'Comment: created'),
        ('COMMENT:UPDATE', 'Comment: updated'),
        ('COMMENT:DELETE', 'Comment: deleted'),

        # Promotions
        ('PROMOTION:CREATE', 'Promotion: created'),
        ('PROMOTION:RETIRE', 'Promotion: retired'),
        ('AD:CREATE', 'Ad: created,'),
        ('AD:UPDATE', 'Ad: update'),
        ('AD:GOLIVE', 'Ad: went live'),
        ('AD:RETIRE', 'Ad: retired'),

        # Publisher pages
        ('PUBLISHER:CREATE', 'Publisher: created'),
        ('PUBLISHER:UPDATE', 'Publisher: updated'),
        ('PUBLISHER:DELETE', 'Publisher: deleted'),
        ('PUBLISHER:VIEW', 'Publisher: viewed'),
        ('PUBLISHER:CLAIMED', 'Publisher: claimed'),

        # Search
        ('SEARCH:SEARCH', 'Search: run'),
    )

    activity_time = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object_model = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, app, action, object_model):
        item_type = "{}:{}".format(app.upper(), action.upper())
        if item_type not in dict(Activity.ACTIVITY_TYPES):
            return  # XXX should we fail silently?
        activity = cls(activity_type=item_type)
        activity.object_model = object_model
        activity.save()

    class Meta:
        ordering = ['-activity_time']
