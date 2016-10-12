from django.conf.urls import url

from .views import front

urlpatterns = [
    url('^$', front, name='front'),
]
