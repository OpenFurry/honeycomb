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
    url('^$', views.view_notifications_ab, name='view_notifications'),
    url('^categories/$', views.view_notifications_categories,
        name='view_notifications_categories'),
    url('^timeline/$', views.view_notifications_timeline,
        name='view_notifications_timeline'),
    url('^timeline/(?P<page>\d+)/$', views.view_notifications_timeline,
        name='view_notifications_timeline'),
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
comment_urls = [
    url('^post/$', views.post_comment, name='post_comment'),
    url('^delete/$', views.delete_comment, name='delete_comment'),
]

urlpatterns = [
    url('^~([^/]+)/', include(user_urls)),
    url('^notifications/', include(notification_urls)),
    url('^comment/', include(comment_urls)),
    url(settings.SUBMISSION_BASE, include(submission_urls)),
]
