from django import template
from django.conf import settings
from django.db.models import (
    Count,
    Max,
    Min,
)

register = template.Library()
TAG_MAX = getattr(settings, 'TAGCLOUD_MAX', 5.0)
TAG_MIN = getattr(settings, 'TAGCLOUD_MIN', 1.0)


def get_weight_closure(tag_min, tag_max, count_min, count_max):
    def weight_closure(count, tag_min=tag_min, tag_max=tag_max,
                       count_min=count_min, count_max=count_max):
        # Prevent a division by zero here, found to occur under some
        # pathological but nevertheless actually occurring circumstances.
        if count_max == count_min:
            factor = 1.0
        else:
            factor = float(tag_max - tag_min) / float(count_max - count_min)

        return tag_max - (count_max - count) * factor
    return weight_closure


@register.assignment_tag
def get_weighted_tags(tags):
    use_count = tags.annotate(use_count=Count('taggit_taggeditem_items'))
    if len(use_count) == 0:
        return tags
    get_weight = get_weight_closure(
        TAG_MIN,
        TAG_MAX,
        use_count.aggregate(Min('use_count'))['use_count__min'],
        use_count.aggregate(Max('use_count'))['use_count__max'])
    tags = use_count.order_by('name')
    for tag in tags:
        tag.weight = get_weight(tag.use_count)
    return tags
