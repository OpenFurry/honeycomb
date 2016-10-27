from django.conf.urls import (
    include,
    url,
)

from . import (
    group_views,
    views,
)

app_name = 'usermgmt'
group_urls = [
    url('^$', group_views.list_groups, name='list_groups'),
    url('^create/$', group_views.create_group, name='create_group'),
    url('^(?P<group_id>\d+)/$', group_views.view_group, name='view_group'),
    url('^(?P<group_id>\d+)/edit/$', group_views.edit_group, name='edit_group'),
    url('^(?P<group_id>\d+)/delete/$', group_views.delete_group,
        name='delete_group'),
]
urlpatterns = [
    url('^register/$', views.Register.as_view(), name='register'),
    url('^accounts/profile/$', views.update_profile, name='update_profile'),
    url('^~([^/]+)/$', views.view_profile, name='view_profile'),
    url('^~(?P<username>[^/]+)/groups/', include(group_urls)),
]
