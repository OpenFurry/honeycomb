from django.conf.urls import (
    include,
    url,
)

from . import views


app_name = 'tags'
tag_views = [
    url('^$', views.view_tag, name='view_tag'),
    url('^(?P<page>\d+)/$', views.view_tag, name='view_tag'),
    url('^favorite/', views.favorite_tag, name='favorite_tag'),
    url('^unfavorite', views.unfavorite_tag, name='unfavorite_tag'),
    url('^block/', views.block_tag, name='block_tag'),
    url('^unblock/', views.unblock_tag, name='unblock_tag'),
]
tags_views = [
    url('^$', views.list_tags, name='list_tags'),
    url('^favorites/$', views.list_submissions_with_favorite_tags,
        name='list_submissions_with_favorite_tags'),
    url('^favorites/(?P<page>\d+)/$',
        views.list_submissions_with_favorite_tags,
        name='list_submissions_with_favorite_tags'),
    url('^tag/(?P<tag_slug>[-\w]+)/', include(tag_views)),
]
categories_views = [
    url('^$', views.list_tags, name='XXX-changeme')
]
urlpatterns = [
    url('^tags/', include(tags_views)),
    url('^categories/', include(categories_views)),
]
