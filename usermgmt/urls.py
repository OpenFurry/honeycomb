from django.conf.urls import url

from . import views

urlpatterns = [
    url('^register/$', views.Register.as_view(), name='register'),
]
