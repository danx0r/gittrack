from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'gittrack.views.home', name='home'),
)
