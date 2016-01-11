from django.conf.urls import include, patterns, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'', include('website.urls')),
    url(r'', include('worms.urls')),
    url(r'', include('clones.urls')),
    url(r'', include('library.urls')),
    url(r'', include('experiments.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login_url'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout_url'),
    url(r'^admin/', admin.site.urls),
)
