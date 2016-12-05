from django.conf.urls import url

from . import views
from api.urls import empty_view


urlpatterns = [
    url('^$', empty_view, name='url'),
    url('^$', empty_view, name='v1.url'),
    url('^user_suggest/$', views.user_suggest, name='user_suggest'),
]
