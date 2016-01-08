from django.conf.urls import url

from worms import views


urlpatterns = [
    url(r'^worm-strains$', views.worms, name='worms_url'),
]
