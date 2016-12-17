import datetime
import json

from django.contrib.auth.models import (
    Group,
    User,
)
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from taggit.models import (
    Tag,
    TaggedItem,
)

from .models import Activity
from administration.models import Flag
from core.templatetags.git_revno import git_revno
from promotion.models import (
    Ad,
    AdLifecycle,
    Promotion,
)
from publishers.models import Publisher
from social.models import (
    Comment,
    EnjoyItem,
    Rating,
)
from submissions.models import (
    Folder,
    Submission,
)
from usermgmt.group_models import FriendGroup


def generate_stream_entry(activity):
    """Generates an entry in the JSON stream of activities.

    This provides more readable results in the stream.

    Args:
        activity: the :model:`activitystream.Activity` object

    Returns:
        A dict containing more readable information
    """
    entry = {
        'time': activity.activity_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'type': activity.activity_type,
    }
    if activity.content_type:
        # Just get the string representation of the object.
        entry['instance'] = "{}: {}".format(
            activity.content_type.name, str(activity.object_model))
    return entry


@cache_page(60 * 15)
def get_stream(request, models=None, object_id=None):
    """View for retrieving the activity stream.

    The stream may be limited to a model, a specific object, or potentially an
    activity type.

    Args:
        request: the Django request object.  If `type` is in request.GET,
            that is used on filtering the response by activity type
        models: a comma separated list of models.  Each entry in the list is
            a tuple in the form of app_label:model.
        object_id: an object ID, such as a submission ID, to be passed with
            models (e.g: models=submissions:submission, object_id=1)

    Returns:
        A JSON object containing the stream.
    """
    stream = Activity.objects.select_related('content_type')

    # Filter on certain content types if provided.
    if models:
        expanded = [model.split(':') for model in models.split(',')]
        ctypes = ContentType.objects.filter(
            app_label__in=[i[0] for i in expanded],
            model__in=[i[1] for i in expanded])
        stream = stream.filter(content_type__in=ctypes)

    # Filter for certain objects if provided.
    if object_id:
        if ',' not in models:
            stream = stream.filter(object_id=object_id)

    # Filter on certain activity types if provided.
    if request.GET.get('type') is not None:
        stream = stream.filter(
            activity_type__in=request.GET['type'].split(','))
    data = []
    for activity in stream:
        data.append(generate_stream_entry(activity))
    return HttpResponse(
        json.dumps(data, separators=[',', ':']),
        content_type='application/json')


def _get_sitewide_data():
    """Builds a dict of data surrounding the site

    This function is fairly expensive and should be wrapped in a view or
    template that caches the results.
    """
    active_promotions = Promotion.objects.filter(
        promotion_end_date__gte=datetime.date.today())
    return {
        'version': git_revno(),
        'users': {
            'all': User.objects.count(),
            'staff': User.objects.filter(is_staff=True).count(),
            'superusers': User.objects.filter(is_superuser=True).count(),
        },
        'groups': dict([(group.name, group.user_set.count())
                        for group in Group.objects.all()]),
        'submissions': Submission.objects.count(),
        'folders': Folder.objects.count(),
        'friendgroups': FriendGroup.objects.count(),
        'ratings': {
            'total': Rating.objects.count(),
            '1star': Rating.objects.filter(rating=1).count(),
            '2star': Rating.objects.filter(rating=2).count(),
            '3star': Rating.objects.filter(rating=3).count(),
            '4star': Rating.objects.filter(rating=4).count(),
            '5star': Rating.objects.filter(rating=5).count(),
        },
        'favorites':
            Activity.objects.filter(activity_type='SOCIAL_FAVORITE').count() -
            Activity.objects.filter(activity_type='SOCIAL_UNFAVORITE').count(),
        'enjoys': EnjoyItem.objects.count(),
        'comments': Comment.objects.count(),
        'tags': {
            'tags': Tag.objects.count(),
            'taggeditems': TaggedItem.objects.count(),
        },
        'publishers': Publisher.objects.count(),
        'promotions': {
            'all_active': active_promotions.count(),
            'promotions':
                active_promotions.filter(
                    promotion_type=Promotion.PROMOTION).count(),
            'paid_promotions':
                active_promotions.filter(
                    promotion_type=Promotion.PAID_PROMOTION).count(),
            'highlight': active_promotions.filter(
                promotion_type=Promotion.HIGHLIGHT).count(),
        },
        'ads': {
            'total': Ad.objects.count(),
            'live': AdLifecycle.objects.filter(live=True).count(),
        },
        'adminflags': Flag.objects.count(),
    }


@cache_page(60 * 60)
def sitewide_data(request):
    """View for retrieving the sitewide data."""
    data = _get_sitewide_data()
    return HttpResponse(
        json.dumps(data, separators=[',', ':']),
        content_type='application/json')
