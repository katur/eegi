from django.conf.urls import patterns, url

urlpatterns = patterns(
    'wormstrains.views',
    url(r'^strains$', 'strains', name='strains_url'),
)
