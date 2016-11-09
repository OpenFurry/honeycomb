from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from administration.models import Ban


def BanMiddleware(get_response):

    def middleware(request):
        response = get_response(request)
        if request.user.is_authenticated and request.user.profile.banned:
            pertinent_ban = Ban.objects.get(user=request.user, active=True)
            return redirect(reverse('administration:ban_notice', kwargs={
                'ban_id': pertinent_ban.id,
                'ban_hash': pertinent_ban.get_ban_hash(),
            }))
        return response

    return middleware
