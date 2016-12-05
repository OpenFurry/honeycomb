import json

from django.contrib.auth.models import User
from django.http import HttpResponse


def jr(content):
    return HttpResponse(json.dumps(content, separators=[',', ':']),
                        content_type='application/json')


def user_suggest(request):
    prefix = request.GET.get('prefix', '')
    if len(prefix) < 3:
        return jr([])
    suggestions = [u.username for
                   u in User.objects.filter(username__startswith=prefix)[:10]]
    return jr(suggestions)
