from django.conf.urls import patterns, url


urlpatterns = patterns(
    'clones.views',
    url(r'^clone_plates$', 'clone_plates', name='clone_plates_url'),
)
