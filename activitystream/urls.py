from django.conf.urls import url

from . import views


app_name = 'activitystream'
urlpatterns = [
    url('^$', views.sitewide_data, name='sitewide_data'),
    url('^stream/$', views.get_stream, name='get_stream'),
    url('^stream/(?P<models>[\w_:]+)/$', views.get_stream, name='get_stream'),
    url('^stream/(?P<models>[\w_:]+)/(?P<object_id>\d+)/$',
        views.get_stream, name='get_stream'),
]
