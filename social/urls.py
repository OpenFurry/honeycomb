from django.conf import settings
from django.conf.urls import (
    include,
    url,
)

from . import views

app_name = 'social'
user_urls = [
    url('^watch/$', views.watch_user, name='watch_user'),
    url('^unwatch/$', views.unwatch_user, name='unwatch_user'),
    url('^block/$', views.block_user, name='block_user'),
    url('^unblock/$', views.unblock_user, name='unblock_user'),
    url('^message/$', views.message_user, name='message_user'),
]
notification_urls = [
    url('^$', views.view_notifications, name='view_notifications'),
    url('^remove/$', views.remove_notifications, name='remove_notifications'),
    url('^nuke/$', views.nuke_notifications, name='nuke_notifications'),
]
submission_urls = [
    url('^favorite/$', views.favorite_submission, name='favorite_submission'),
    url('^unfavorite/$', views.unfavorite_submission,
        name='unfavorite_submission'),
    url('^rate/$', views.rate_submission, name='rate_submission'),
    url('^enjoy/$', views.enjoy_submission, name='enjoy_submission'),
]

urlpatterns = [
    url('^~([^/]+)/', include(user_urls)),
    url('^notifications/', include(notification_urls)),
    url(settings.SUBMISSION_BASE, include(submission_urls)),
]
