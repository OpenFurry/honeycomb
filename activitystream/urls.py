from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.sitewide_data, name='sitewide_data'),
    url('^stream/$', views.get_stream, name='get_stream'),
]
