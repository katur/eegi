from django.conf.urls import patterns, url


urlpatterns = patterns(
    'worms.views',
    url(r'^worm-strains$', 'worm_strains', name='worm_strains_url'),
)
