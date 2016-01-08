from django.conf.urls import url

from experiments import views


urlpatterns = [
    url(r'^experiment/(\d+_[A-H]\d\d)$', views.experiment,
        name='experiment_url'),
    url(r'^experiment/(\d+_[A-H]\d\d)/toggle-junk$',
        views.experiment_toggle_junk,
        name='experiment_toggle_junk_url'),
    url(r'^experiment/(\d+)$', views.experiment_plate,
        name='experiment_plate_url'),

    url(r'^experiments$', views.experiments,
        name='experiments_url'),
    url(r'^experiment-plates$', views.experiment_plates,
        name='experiment_plates_url'),
    url(r'^experiment-plates-vertical/([\d,]+)$',
        views.experiment_plates_vertical,
        name='experiment_plates_vertical_url'),

    url(r'^single-knockdown$', views.single_knockdown_search,
        name='single_knockdown_search_url'),
    url(r'^rnai-knockdown/([^/]+)$', views.rnai_knockdown,
        name='rnai_knockdown_url'),
    url(r'^rnai-knockdown/([^/]+)/([^/]+)$', views.rnai_knockdown,
        name='rnai_knockdown_url'),
    url(r'^mutant-knockdown/([^/]+)/([^/]+)$', views.mutant_knockdown,
        name='mutant_knockdown_url'),
    url(r'^double-knockdown$', views.double_knockdown_search,
        name='double_knockdown_search_url'),
    url(r'^double-knockdown/([^/]+)/([^/]+)/([^/]+)$',
        views.double_knockdown,
        name='double_knockdown_url'),

    url(r'^secondary-scores$', views.secondary_scores_search,
        name='secondary_scores_search_url'),
    url(r'^secondary-scores/([^/]+)/([^/]+)$', views.secondary_scores,
        name='secondary_scores_url'),

    url(r'^devstar-scoring-categories$', views.devstar_scoring_categories,
        name='devstar_scoring_categories_url'),
    url(r'^devstar-scoring-category/([^/]+)',
        views.devstar_scoring_category,
        name='devstar_scoring_category_url'),
]
