from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
        url(r'^_admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    url('^', include('usermgmt.urls')),
    url('^', include('app.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
