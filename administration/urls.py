from django.conf.urls import (
    include,
    url,
)

from . import views


app_name = 'administration'
application_urls = [
    url('^$', views.list_all_applications, name='list_all_applications'),
    url('^mine/$', views.list_participating_applications,
        name='list_participating_applications'),
    url('^social/$', views.list_social_applications,
        name='list_social_applications'),
    url('^content/$', views.list_content_applications,
        name='list_content_applications'),
    url('^create/$', views.create_application, name='create_application'),
    url('^application/(?P<application_id>\d+)/$', views.view_application,
        name='view_application'),
    url('^application/(?P<application_id>\d+)/resolve/$',
        views.claim_application, name='claim_application'),
    url('^application/(?P<application_id>\d+)/resolve/$',
        views.resolve_application, name='resolve_application'),
]
flag_urls = [
    url('^$', views.list_all_flags, name='list_all_flags'),
    url('^mine/$', views.list_participating_flags,
        name='list_participating_flags'),
    url('^social/$', views.list_social_flags,
        name='list_social_flags'),
    url('^content/$', views.list_content_flags,
        name='list_content_flags'),
    url('^create/$', views.create_flag, name='create_flag'),
    url('^flag/(?P<flag_id>\d+)/$', views.view_flag,
        name='view_flag'),
    url('^flag/(?P<flag_id>\d+)/resolve/$',
        views.claim_flag, name='claim_flag'),
    url('^flag/(?P<flag_id>\d+)/resolve/$',
        views.resolve_flag, name='resolve_flag'),
]
ban_urls = [
    url('^$', views.list_bans, name='list_bans'),
    url('^mine/$', views.list_participating_bans,
        name='list_participating_bans'),
    url('^create/$', views.create_ban, name='create_ban'),
    url('^ban/(?P<ban_id>\d+)/$', views.view_ban,
        name='view_ban'),
    url('^ban/(?P<ban_id>\d+)/lift/$', views.lift_ban, name='lift_ban'),
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
