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
from publishers.models import PublisherPage
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
    entry = {
        'time': activity.activity_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'type': activity.activity_type,
    }
    if activity.content_type:
        entry['instance'] = "{}: {}".format(
            activity.content_type.name, str(activity.object_model))
    return entry


@cache_page(60 * 15)
def get_stream(request, models=None, object_id=None):
    stream = Activity.objects.select_related('content_type')
    if models:
        expanded = [model.split(':') for model in models.split(',')]
        ctypes = ContentType.objects.filter(
            app_label__in=[i[0] for i in expanded],
            model__in=[i[1] for i in expanded])
        stream = stream.filter(content_type__in=ctypes)
    if object_id:
        if ',' not in models:
            stream = stream.filter(object_id=object_id)
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
    active_promotions = Promotion.objects.filter(
        promotion_end_date__date__gte=datetime.datetime.now())
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
        'publishers': PublisherPage.objects.count(),
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
    data = _get_sitewide_data()
    return HttpResponse(
        json.dumps(data, separators=[',', ':']),
        content_type='application/json')
