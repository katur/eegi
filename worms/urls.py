from django.conf.urls import patterns, url


urlpatterns = patterns(
    'worms.views',
    url(r'^worm-strains$', 'worms', name='worms_url'),
)
