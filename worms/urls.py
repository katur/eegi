from django.conf.urls import patterns, url


urlpatterns = patterns(
    'worms.views',
    url(r'^worm_strains$', 'worm_strains', name='worm_strains_url'),
)
