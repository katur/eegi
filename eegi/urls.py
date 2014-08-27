from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'', include('website.urls')),
    url(r'', include('worms.urls')),
    url(r'', include('library.urls')),
    url(r'', include('experiments.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
