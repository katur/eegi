from django.conf.urls import patterns, url


urlpatterns = patterns(
    'experiments.views',
    url(r'^experiments$',
        'experiments', name='experiments_url'),
    url(r'^experiment/(\d+)$',
        'experiment_plate', name='experiment_plate_url'),
    url(r'^experiment-vertical/(\d+)$',
        'experiment_plate_vertical', name='experiment_plate_vertical_url'),
    url(r'^experiment/(\d+)/([A-H]\d+)$',
        'experiment_well', name='experiment_well_url'),
    url(r'^double-knockdown$',
        'double_knockdown_search', name='double_knockdown_search_url'),
    url(r'^double-knockdown/([^/]+)/([^/]+)/([^/]+)$',
        'double_knockdown', name='double_knockdown_url'),
)
