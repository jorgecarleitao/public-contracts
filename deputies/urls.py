from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from . import views
from . import views_data


urlpatterns = patterns('',
                       url(r'^%s/%s$' % (_('deputies'), _('home')), views.home, name='deputies_home'),
                       url(r'^%s$' % _('deputies'), views.deputies_list, name='deputies_deputies'),
                       url(r'^%s$' % _('parties'), views.parties_list, name='deputies_parties'),
                       url(r'^%s/(\d+)$' % _('party'), views.party_view, name='party_view'),

                       url(r'^%s/%s$' % (_('deputies'), _('analysis')),
                           views.analysis_list, name='deputies_analysis'),

                       url(r'^%s/%s/(\d+)/(\w+)' % (_('deputies'), _('analysis')),
                           views.analysis, name='deputies_analysis_selector'),
                       url(r'^%s/%s/(\d+)' % (_('deputies'), _('analysis')),
                           views.analysis, name='deputies_analysis_internal_selector',
                           ),

                       url(r'^%s/%s/([-\w]+)/data' % (_('deputies'), _('analysis')),
                           views_data.analysis_selector, name='deputies_data_selector',
                           ),
                       )
