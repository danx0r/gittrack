from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'gittrack.views.home', name='home'),
    url(r'^iss$', 'gittrack.views.view_issue', name='iss'),
    url(r'^top$', 'gittrack.views.view_top', name='top'),
)
