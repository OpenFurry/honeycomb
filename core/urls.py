from django.conf.urls import url

from .views import (
    BasicSearchView,
    flatpage_list,
    front,
    helppage_list,
)

app_name = 'core'
urlpatterns = [
    url('^$', front, name='front'),
    url('^about/$', flatpage_list, name='flatpage_list'),
    url('^about/help/$', helppage_list, name='helppage_list'),
    url('^search/$', BasicSearchView.as_view(), name='basic_search'),
]
