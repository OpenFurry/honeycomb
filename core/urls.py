from django.conf.urls import url

from .views import (
    flatpage_list,
    front,
)

app_name = 'core'
urlpatterns = [
    url('^$', front, name='front'),
    url('^about/$', flatpage_list, name="flatpage_list"),
]
