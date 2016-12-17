from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from six.moves.urllib import parse

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def campaignify(value, medium_campaign):
    medium, campaign = medium_campaign.split(',', 1)
    params = {
        'utm_source': settings.UTM_SOURCE,
        'utm_medium': medium,
        'utm_campaign': campaign,
    }

    url_parts = list(parse.urlparse(value))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = parse.urlencode(query)
    return(parse.urlunparse(url_parts))
