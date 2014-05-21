from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns(
    '',
    url(r'', include('website.urls')),
    url(r'', include('wormstrains.urls')),
    url(r'', include('clones.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
