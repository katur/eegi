from django.conf.urls import patterns, url


urlpatterns = patterns(
    'library.views',
    url(r'^library-plates$', 'library_plates', name='library_plates_url'),
    url(r'^library-plate/(?P<id>.*)$', 'library_plate',
        name='library_plate_url'),
)
