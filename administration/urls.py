from django.conf.urls import (
    include,
    url,
)

from . import (
    application_views,
    ban_views,
    flag_views,
    views,
)


app_name = 'administration'
application_urls = [
    url('^$', application_views.list_all_applications,
        name='list_all_applications'),
    url('^mine/$', application_views.list_participating_applications,
        name='list_participating_applications'),
    url('^social/$', application_views.list_social_applications,
        name='list_social_applications'),
    url('^content/$', application_views.list_content_applications,
        name='list_content_applications'),
    url('^create/$', application_views.create_application,
        name='create_application'),
    url('^application/(?P<application_id>\d+)/$',
        application_views.view_application,
        name='view_application'),
    url('^application/(?P<application_id>\d+)/claim/$',
        application_views.claim_application, name='claim_application'),
    url('^application/(?P<application_id>\d+)/resolve/$',
        application_views.resolve_application, name='resolve_application'),
]
flag_urls = [
    url('^$', flag_views.list_all_flags, name='list_all_flags'),
    url('^mine/$', flag_views.list_participating_flags,
        name='list_participating_flags'),
    url('^social/$', flag_views.list_social_flags,
        name='list_social_flags'),
    url('^content/$', flag_views.list_content_flags,
        name='list_content_flags'),
    url('^create/$', flag_views.create_flag, name='create_flag'),
    url('^flag/(?P<flag_id>\d+)/$', flag_views.view_flag,
        name='view_flag'),
    url('^flag/(?P<flag_id>\d+)/join/$',
        flag_views.join_flag, name='join_flag'),
    url('^flag/(?P<flag_id>\d+)/resolve/$',
        flag_views.resolve_flag, name='resolve_flag'),
]
ban_urls = [
    url('^$', ban_views.list_bans, name='list_bans'),
    url('^notice/(?P<ban_id>\d+)/(?P<ban_hash>.+)/$', ban_views.ban_notice,
        name='ban_notice'),
    url('^mine/$', ban_views.list_participating_bans,
        name='list_participating_bans'),
    url('^create/$', ban_views.create_ban, name='create_ban'),
    url('^ban/(?P<ban_id>\d+)/$', ban_views.view_ban,
        name='view_ban'),
    url('^ban/(?P<ban_id>\d+)/lift/$', ban_views.lift_ban, name='lift_ban'),
]
admin_urls = [
    url('^$', views.dashboard, name='dashboard'),
    url('^applications/', include(application_urls)),
    url('^flags/', include(flag_urls)),
    url('^bans/', include(ban_urls)),
]
urlpatterns = [
    url('^admin/', include(admin_urls)),
]
