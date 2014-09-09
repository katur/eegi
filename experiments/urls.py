from django.conf.urls import patterns, url


urlpatterns = patterns(
    'experiments.views',
    url(r'^experiments$', 'experiments', name='experiments_url'),
    url(r'^experiment/(?P<id>[0-9]+)$', 'experiment',
        name='experiment_url'),
    url(r'^experiment-range/(?P<start>[0-9]+)/(?P<end>[0-9]+)$',
        'experiment_range', name='experiment_range_url'),
)
