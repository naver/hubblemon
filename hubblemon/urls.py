from django.conf.urls import patterns, include, url
from django.contrib import admin

#from graph.views import *
from chart.views import *

import os.path

site_media = os.path.join(os.path.dirname(__file__), 'site_media')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hubblemon.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', chart_page),
    url(r'^graph/', graph_page),
    url(r'^expr/', expr_page),
    url(r'^chart/', chart_page),
    url(r'^query/', query_page),
    url(r'^system/', system_page),
    url(r'^addon/', addon_page),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': site_media }),
)

