from django.conf import settings
from django.conf.urls import (
    include,
    url,
)

from . import (
    folder_views,
    views,
)

app_name = 'submissions'
full_folder_patterns = [
    url('^$', folder_views.view_folder, name='view_folder'),
    url('^page/(?P<page>\d+)/', folder_views.view_folder, name='view_folder'),
    url('^edit/$', folder_views.update_folder, name='update_folder'),
    url('^delete/$', folder_views.delete_folder, name='delete_folder'),
    url('^reorder/$', folder_views.update_submission_order_in_folder,
        name='update_submission_order_in_folder'),
]
folder_patterns = [
    url('^$', folder_views.view_root_level_folders,
        name='view_root_level_folders'),
    url('^page/(?P<page>\d+)/$', folder_views.view_root_level_folders,
        name='view_root_level_folders'),
    url('^create/$', folder_views.create_folder, name='create_folder'),
    url('^(?P<folder_id>\d+)/$', folder_views.view_folder, name='view_folder'),
    url('^(?P<folder_id>\d+)-(?P<folder_slug>[-\w]+)/',
        include(full_folder_patterns))
]
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
    url('^~(?P<username>[^/]+)/submissions/page/(?P<page>\d+)/$',
        views.list_user_submissions, name='list_user_submissions'),
    url('^~(?P<username>[^/]+)/favorites/$',
        views.list_user_favorites, name='list_user_favorites'),
    url('^~(?P<username>[^/]+)/favorites/page/(?P<page>\d+)/$',
        views.list_user_favorites, name='list_user_favorites'),
    url('^~(?P<username>[^/]+)/folders/', include(folder_patterns)),
]
