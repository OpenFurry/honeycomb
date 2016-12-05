from django.conf.urls import (
    include,
    url,
)

from . import views


app_name = 'publishers'
news_patterns = [
    url(r'^$', views.list_news_items, name='list_news_items'),
    url(r'^page/(?P<page>\d+)/$', views.list_news_items,
        name='list_news_items'),
    url(r'^create/$', views.create_news_item, name='create_news_item'),
    url(r'^(?P<item_id>\d+)/$', views.view_news_item, name='view_news_item'),
    url(r'^(?P<item_id>\d+)/edit/$', views.edit_news_item,
        name='edit_news_item'),
    url(r'^(?P<item_id>\d+)/delete/$', views.delete_news_item,
        name='delete_news_item'),
]
publisher_patterns = [
    url(r'^$', views.view_publisher, name='view_publisher'),
    url(r'^news/', include(news_patterns)),
    url(r'^edit/$', views.edit_publisher, name='edit_publisher'),
    url(r'^delete/$', views.delete_publisher, name='delete_publisher'),
    url(r'^members/add/$', views.add_member, name='add_member'),
    url(r'^members/remove/$', views.remove_member, name='remove_member'),
    url(r'^editors/add/$', views.add_editor, name='add_editor'),
    url(r'^editors/remove/$', views.remove_editor, name='remove_editor'),
    url(r'^calls/$', views.list_calls, name='list_calls'),
    url(r'^calls/add/$', views.add_call, name='add_call'),
    url(r'^calls/remove/$', views.remove_call, name='remove_call'),
    url(r'^ownership/change/$', views.change_ownership,
        name='change_ownership'),
]
urlpatterns = [
    url(r'^publishers/$', views.list_publishers, name='list_publishers'),
    url(r'^publishers/(?P<page>\d+)/$', views.list_publishers,
        name='list_publishers'),
    url(r'^publishers/create/$', views.create_publisher,
        name='create_publisher'),
    url(r'^publisher/(?P<publisher_slug>[-_\w]+)/',
        include(publisher_patterns)),
]
