from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import views

urlpatterns = patterns('',
                       url(r'^$', views.law_list, name='law_law_list'),
)
