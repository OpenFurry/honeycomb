from django.conf.urls import url

from . import views

urlpatterns = [
    url('^register/$', views.Register.as_view(), name='register'),
    url('^accounts/profile/$', views.update_profile, name='update_profile'),

    url('^~([^/]+)/$', views.view_profile, name='view_profile'),
]
