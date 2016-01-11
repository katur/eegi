from django.conf.urls import include, url
from django.contrib import admin, auth
from django.contrib.auth.views import login, logout


admin.autodiscover()


urlpatterns = [
    url(r'', include('website.urls')),
    url(r'', include('worms.urls')),
    url(r'', include('clones.urls')),
    url(r'', include('library.urls')),
    url(r'', include('experiments.urls')),
    url(r'^login/$', auth.views.login,
        {'template_name': 'login.html'}, name='login_url'),
    url(r'^logout/$', auth.views.logout,
        {'next_page': '/'}, name='logout_url'),
    url(r'^admin/', admin.site.urls),
]
