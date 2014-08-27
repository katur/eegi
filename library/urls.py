from django.conf.urls import patterns, url


urlpatterns = patterns(
    'library.views',
    url(r'^library_plates$', 'library_plates', name='library_plates_url'),
)
