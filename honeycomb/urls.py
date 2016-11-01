from django.conf import settings
from django.conf.urls import (
    include,
    url,
)
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    url(r'^_admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    url('^', include('usermgmt.urls')),
    url('^', include('social.urls')),
    url('^', include('core.urls')),
    url('^', include('submissions.urls')),
    url('^', include('tags.urls')),
    url('^activity/', include('activitystream.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
