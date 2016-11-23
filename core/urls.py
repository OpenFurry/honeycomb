from django.conf.urls import (
    include,
    url,
)

from .views import (
    flatpage_list,
    front,
    helppage_list,
)

app_name = 'core'
urlpatterns = [
    url('^$', front, name='front'),
    url('^about/$', flatpage_list, name='flatpage_list'),
    url('^about/help/$', helppage_list, name='helppage_list'),
    url('^search/', include('haystack.urls')),
]
