from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^experiment/(\d+_[A-H]\d\d)/$', views.experiment_well,
        name='experiment_well_url'),
    url(r'^experiment/(\d+)/$', views.experiment_plate,
        name='experiment_plate_url'),
    url(r'^vertical-experiment-plates/([\d,]+)/$',
        views.vertical_experiment_plates,
        name='vertical_experiment_plates_url'),

    url(r'^find-experiment-wells/$', views.find_experiment_wells,
        name='find_experiment_wells_url'),
    url(r'^find-experiment-plates/$', views.find_experiment_plates,
        name='find_experiment_plates_url'),

    url(r'^new-experiment-plate/$', views.new_experiment_plate_and_wells,
        name='new_experiment_plate_and_wells_url'),

    url(r'^single-knockdown/$', views.single_knockdown_search,
        name='single_knockdown_search_url'),
    url(r'^rnai-knockdown/([^/]+)/$', views.rnai_knockdown,
        name='rnai_knockdown_url'),
    url(r'^rnai-knockdown/([^/]+)/([^/]+)/$', views.rnai_knockdown,
        name='rnai_knockdown_url'),
    url(r'^mutant-knockdown/([^/]+)/([^/]+)/$', views.mutant_knockdown,
        name='mutant_knockdown_url'),
    url(r'^double-knockdown/$', views.double_knockdown_search,
        name='double_knockdown_search_url'),
    url(r'^double-knockdown/([^/]+)/([^/]+)/([^/]+)/$',
        views.double_knockdown, name='double_knockdown_url'),

    url(r'^secondary-scores/$', views.secondary_scores_search,
        name='secondary_scores_search_url'),
    url(r'^secondary-scores/([^/]+)/([^/]+)/$', views.secondary_scores,
        name='secondary_scores_url'),

    url(r'^image-categories/$', views.image_categories,
        name='image_categories_url'),
    url(r'^image-category/([^/]+)/$', views.image_category,
        name='image_category_url'),
]
