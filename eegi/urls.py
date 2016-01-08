from django.conf.urls import include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = [
    url(r'', include('website.urls')),
    url(r'', include('worms.urls')),
    url(r'', include('clones.urls')),
    url(r'', include('library.urls')),
    url(r'', include('experiments.urls')),
    url(r'^admin/', admin.site.urls),
]
