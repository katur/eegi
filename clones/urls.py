from django.conf.urls import patterns, url


urlpatterns = patterns(
    'clones.views',
    url(r'^clones$', 'clones', name='clones_url'),
)
