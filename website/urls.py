from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.home, name='home_url'),
    url(r'^help/$', views.help_page, name='help_url'),
]
