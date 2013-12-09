from django.conf.urls import patterns, include, url


# Uncomment the next two lines to enable the admin:
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ProjectFolder.views.home', name='home'),
    # url(r'^ProjectFolder/', include('ProjectFolder.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^preview/', include('template_previewer.urls')),
    #url(r'^templatepreview/', include('previewer.urls')),
    
    url(r'^docreader/', include('docreader.urls',namespace="docreader")),
    url(r'^enersectapp/', include('enersectapp.urls',namespace="enersectapp")),
    url(r'^admin/', include(admin.site.urls)),
)
