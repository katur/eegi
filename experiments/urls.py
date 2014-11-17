from django.conf.urls import patterns, url


urlpatterns = patterns(
    'experiments.views',
    url(r'^experiments$',
        'experiments', name='experiments_url'),
    url(r'^experiment/(?P<id>[0-9]+)$',
        'experiment', name='experiment_url'),
    url(r'^experiment_tile_view/(?P<id>[0-9]+)$',
        'experiment_tile_view', name='experiment_tile_view_url'),
    url(r'^experiment/(?P<id>[0-9]+)/(?P<well>[A-H][0-9]+)$',
        'experiment_well', name='experiment_well_url'),
    url(r'^double-knockdown$',
        'double_knockdown_search', name='double_knockdown_search_url'),
    url(r'^double-knockdown/(?P<strain>[^/]+)/(?P<clone>[^/]+)/(?P<temperature>[^/]+)$',
        'double_knockdown', name='double_knockdown_url'),
)
