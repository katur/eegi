from django.conf.urls import patterns, url


urlpatterns = patterns(
    'experiments.views',
    url(r'^experiments/(?P<start>[0-9]+)/(?P<end>[0-9]+)$', 'experiments',
        name='experiments_url'),
)
