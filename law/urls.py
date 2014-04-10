from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import views

urlpatterns = patterns('',
                       url(r'^%s/%s$' % (_('law'), _('home')), views.home, name='law_home'),
                       url(r'^%s$' % _('law'), views.law_list, name='law_law_list'),
                       url(r'^%s$' % _('types'), views.types_list, name='law_types_list'),
                       url(r'^%s/(\d+)$' % _('type'), views.type_view, name='law_type'),
)
