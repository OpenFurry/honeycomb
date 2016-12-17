from django.conf.urls import (
    include,
    url,
)


def empty_view(request):
    pass


app_name = 'api'
urlpatterns = [
    url('^$', empty_view, name='root.url'),
    url('^v1/', include('api.v1.urls')),
]
