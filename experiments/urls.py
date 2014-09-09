from django.conf.urls import patterns, url


urlpatterns = patterns(
    'experiments.views',
    url(r'^experiments$', 'experiments', name='experiments_url'),
    url(r'^experiment/(?P<id>[0-9]+)$', 'experiment',
        name='experiment_url'),
)
