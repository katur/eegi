from django.conf.urls import patterns, url


urlpatterns = patterns(
    'experiments.views',
    url(r'^experiment/(\d+)$', 'experiment_plate',
        name='experiment_plate_url'),
    url(r'^experiment/(\d+_[A-H]\d\d)$', 'experiment',
        name='experiment_url'),
    url(r'^experiment-plates-vertical/([\d,]+)$',
        'experiment_plates_vertical',
        name='experiment_plates_vertical_url'),

    url(r'^experiment-plates$', 'experiment_plates',
        name='experiment_plates_url'),
    url(r'^experiments$', 'experiments',
        name='experiments_url'),

    url(r'^single-knockdown$', 'single_knockdown_search',
        name='single_knockdown_search_url'),
    url(r'^rnai-knockdown/([^/]+)$', 'rnai_knockdown',
        name='rnai_knockdown_url'),
    url(r'^rnai-knockdown/([^/]+)/([^/]+)$', 'rnai_knockdown',
        name='rnai_knockdown_url'),
    url(r'^mutant-knockdown/([^/]+)/([^/]+)$', 'mutant_knockdown',
        name='mutant_knockdown_url'),
    url(r'^double-knockdown$', 'double_knockdown_search',
        name='double_knockdown_search_url'),
    url(r'^double-knockdown/([^/]+)/([^/]+)/([^/]+)$', 'double_knockdown',
        name='double_knockdown_url'),

    url(r'^secondary-scores$', 'secondary_scores_search',
        name='secondary_scores_search_url'),
    url(r'^secondary-scores/([^/]+)/([^/]+)$', 'secondary_scores',
        name='secondary_scores_url'),

    url(r'^devstar-scoring-categories$', 'devstar_scoring_categories',
        name='devstar_scoring_categories_url'),
    url(r'^devstar-scoring-category/([^/]+)', 'devstar_scoring_category',
        name='devstar_scoring_category_url'),
)
