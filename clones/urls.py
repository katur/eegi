from django.conf.urls import url

from clones import views


urlpatterns = [
    url(r'^clones$', views.clones, name='clones_url'),
    url(r'^clone/([^/]*)$', views.clone, name='clone_url'),
]
