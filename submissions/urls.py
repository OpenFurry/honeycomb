from django.conf import settings
from django.conf.urls import (
    include,
    url,
)

from . import views

app_name = 'submissions'
submission_patterns = [
    url('^$', views.view_submission, name='view_submission'),
    url('^edit/$', views.edit_submission, name='edit_submission'),
    url('^delete/$', views.delete_submission, name='delete_submission'),
]
urlpatterns = [
    url('^submit/$', views.submit, name='submit'),
    url('^(?P<submission_id>\d+)/$', views.view_submission,
        name='view_submission'),
    url(settings.SUBMISSION_BASE, include(submission_patterns)),
    url('^~(?P<username>[^/]+)/submissions/$',
        views.list_user_submissions, name='list_user_submissions'),
    url('^~(?P<username>[^/]+)/submissions/(?P<page>\d+)/$',
        views.list_user_submissions, name='list_user_submissions'),
    url('^~(?P<username>[^/]+)/favorites/$',
        views.list_user_favorites, name='list_user_favorites'),
    url('^~(?P<username>[^/]+)/favorites/(?P<page>\d+)/$',
        views.list_user_favorites, name='list_user_favorites'),
]
