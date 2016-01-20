from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^library-plates/$', views.library_plates,
        name='library_plates_url'),
    url(r'^library-plate/([^/]*)/$', views.library_plate,
        name='library_plate_url'),
]
