from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^worm-strains/$', views.worms, name='worms_url'),
]
