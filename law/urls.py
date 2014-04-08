from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import views

urlpatterns = patterns('',
                       url(r'^/%s$' % _('home'), views.home, name='law_home'),
                       url(r'^$', views.law_list, name='law_law_list'),
                       url(r'^/%s$' % _('types'), views.types_list, name='law_types_list'),
)
