from django.conf.urls.defaults import *
import os
import followup.views as views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",

    # Dashboard
        (r'^$', views.index),
    

    # Send SMS message to reporters 
        (r'^send_sms/$', views.send_sms),

    # Mothers registered 
        (r'^mothers/$', views.mothers),

    # Mother's detail information
        (r'^mother/(?P<mother_id>\d+)/$', views.mother),

    # Centers registered 
        (r'^centers/$', views.health_centers),

    # Health professionals registered 
        (r'^health_profs/$', views.health_profs),


    
    # Display admin page
        #(r'^admin/$', include(admin.site.urls)),

                       
)

