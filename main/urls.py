from django.conf.urls import patterns, include, url

import contracts.urls
import views

urlpatterns = patterns('',
                       url(r'^', include(contracts.urls)),
                       (r'^robots\.txt$', views.robots),
                       )
