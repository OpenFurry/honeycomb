from django.conf.urls import url

from .views import front

app_name = 'core'
urlpatterns = [
    url('^$', front, name='front'),
]
