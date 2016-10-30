import json

from django.contrib.auth.models import (
    Group,
    User,
)
from django.contrib.contenttypes.models import ContentType
from django.http import (HttpResponse)
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from taggit.models import (
    Tag,
    TaggedItem,
)

from .models import Activity
from administration.models import Flag
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


def generate_stream_entry(activity, ctype, instance):
    entry = {
        'time': activity.activity_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'type': activity.activity_type,
    }
    if instance is not None:
        entry['instance'] = "{}: {}".format(ctype.name, str(instance))
    elif activity.content_type:
        entry['instance'] = "{}: {}".format(
            activity.content_type.name, str(activity.object_model))
    return entry


@cache_page(60 * 5)
def get_stream(request, app_label=None, model=None, object_id=None):
    ctype = None
    instance = None
    stream = Activity.objects.select_related('content_type')
    if app_label and model:
        ctype = get_object_or_404(ContentType,
                                  app_label=app_label, model=model)
        stream = stream.filter(content_type=ctype)
    if object_id:
        stream = stream.filter(object_id=object_id)
        instance = ctype.get_object_for_this_type(pk=object_id)
    if request.GET.get('type') is not None:
        stream = stream.filter(activity_type=request.GET['type'])
    data = []
    for activity in stream:
        print(ctype)
        data.append(generate_stream_entry(activity, ctype, instance))
    return HttpResponse(
        json.dumps(data, separators=[',', ':']),
        content_type='application/json')


@cache_page(60 * 60)
def sitewide_data(request):
    data = {
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
            '1-star': Rating.objects.filter(rating=1).count(),
            '2-star': Rating.objects.filter(rating=2).count(),
            '3-star': Rating.objects.filter(rating=3).count(),
            '4-star': Rating.objects.filter(rating=4).count(),
            '5-star': Rating.objects.filter(rating=5).count(),
        },
        'favorites':
            Activity.objects.filter(activity_type='SOCIAL_FAVORITE').count() -
            Activity.objects.filter(activity_type='SOCIAL_UNFAVORITE').count(),
        'enjoys': EnjoyItem.objects.count(),
        'comments': Comment.objects.count(),
        'publishers': PublisherPage.objects.count(),
        'promotions': {
            'promotions':
                Promotion.objects.filter(
                    promotion_type=Promotion.PROMOTION).count(),
            'paid_promotions':
                Promotion.objects.filter(
                    promotion_type=Promotion.PAID_PROMOTION).count(),
            'highlight': Promotion.objects.filter(
                promotion_type=Promotion.HIGHLIGHT).count(),
        },
        'ads': {
            'total': Ad.objects.count(),
            'live': AdLifecycle.objects.filter(live=True).count(),
        },
        'tags': {
            'tags': Tag.objects.count(),
            'taggeditems': TaggedItem.objects.count(),
        },
        'adminflags': Flag.objects.count(),
    }
    return HttpResponse(
        json.dumps(data, separators=[',', ':']),
        content_type='application/json')
