from django.conf import settings
from django.conf.urls import (
    include,
    url,
)
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # Django app urls
    url(r'^_admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^_admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),

    # Honeycomb app urls
    url('^', include('administration.urls')),
    url('^', include('usermgmt.urls')),
    url('^', include('social.urls')),
    url('^', include('core.urls')),
    url('^', include('publishers.urls')),
    url('^', include('submissions.urls')),
    url('^', include('tags.urls')),
    url('^activity/', include('activitystream.urls')),
    url('^calls/', include('submitify.urls')),
    url('^api/', include('api.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
