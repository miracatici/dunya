from django.conf.urls import patterns, url

from makam import views

urlpatterns = patterns('',
    url(r'^$', views.main),
)
