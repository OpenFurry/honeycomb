from django.conf.urls import include, url
from django.contrib import admin

from .views import front

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    url('^', include('usermgmt.urls')),
    url('^$', front, name='front'),
]
