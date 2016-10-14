from django.conf.urls import url

from . import views

urlpatterns = [
    url('^~([^/]+)/watch/$', views.watch_user, name='watch_user'),
    url('^~([^/]+)/unwatch/$', views.unwatch_user, name='unwatch_user'),
    url('^~([^/]+)/block/$', views.block_user, name='block_user'),
    url('^~([^/]+)/unblock/$', views.unblock_user, name='unblock_user'),
    url('^~([^/]+)/message/$', views.message_user, name='message_user'),
]
