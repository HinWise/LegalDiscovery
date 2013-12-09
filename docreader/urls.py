#This is the nathanapp urls file

from django.conf.urls import patterns, url

from docreader import views

urlpatterns = patterns('',
    

    # ex: /doctoreadtool/
    url(r'^doctoreadtool/$', views.doctoreadtool, name='doctoreadtool'),
    
        
        # ex: /doctoreadtool_savedata/
        url(r'^doctoreadtool_savedata/$', views.doctoreadtool_savedata, name='doctoreadtool_savedata'),
        
        
    
)
