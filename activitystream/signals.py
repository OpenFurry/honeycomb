from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
)
from django.db.models.signals import (
    post_delete,
    post_save,
)
from django.dispatch import receiver
from taggit.models import TaggedItem

from .models import Activity
from usermgmt.models import Profile


@receiver(post_save, sender=Profile)
def log_user_register(sender, **kwargs):
    if kwargs['created']:
        Activity.create('user', 'reg', kwargs['instance'].user)


@receiver(user_logged_in)
def log_login(sender, **kwargs):
    """Creates an activity when a user logs in."""
    Activity.create('user', 'login', kwargs['user'])


@receiver(user_logged_out)
def log_logout(sender, **kwargs):
    """Creates an activity when a user logs out."""
    Activity.create('user', 'logout', kwargs['user'])


@receiver(post_save)
def log_base_create_or_update(sender, **kwargs):
    """Attempts to create an activity whenever a model is saved.

    If the model does not exist in the map of valid models, it exits without
    creating anything.
    """
    try:
        name = {
            'Application': 'adminapplication',
            'Ban': 'adminban',
            'Comment': 'comment',
            'Flag': 'adminflag',
            'Folder': 'folder',
            'FriendGroup': 'group',
            'Profile': 'profile',
            'Publisher': 'publisher',
            'Submission': 'submission',
            'Tag': 'tag',
        }[sender.__name__]
    except:
        return
    if name == 'profile' and kwargs['created']:
        return
    Activity.create(
        name,
        'create' if kwargs['created'] else 'update',
        kwargs['instance'])


@receiver(post_delete)
def log_base_delete(sender, **kwargs):
    """Attempts to create an activity whenever a model is deleted.

    If the model does not exist in the map of valid models, it exits without
    creating anything.
    """
    try:
        name = {
            'Application': 'adminapplication',
            'Ban': 'adminban',
            'Flag': 'adminflag',
            'Folder': 'folder',
            'FriendGroup': 'group',
            'Submission': 'submission',
            'Publisher': 'publisher',
        }[sender.__name__]
    except:
        return
    Activity.create(name, 'delete', kwargs['instance'])


@receiver(post_save, sender=TaggedItem)
def log_tagged_item(sender, **kwargs):
    """Creates an activity when a tag is saved."""
    Activity.create(
        'tag',
        'tag' if kwargs['created'] else 'update',
        kwargs['instance'])
