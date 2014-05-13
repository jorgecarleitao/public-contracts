from django.conf.urls import patterns, url
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from . import views

urlpatterns = patterns('',
                       url(r'^%s/%s$' % (_('law'), _('home')), views.home, name='law_home'),
                       url(r'^%s/%s$' % (_('law'), _('analysis')), views.analysis, name='law_analysis'),

                       url(r'^%s/%s/%s$' % (_('law'), _('analysis'),
                                            slugify(_('Impact of EU Law in the Portuguese Law'))),
                           views.law_analysis_eu_impact, name='law_analysis_eu_impact'),

                       url(r'^%s/%s/%s$' % (_('law'), _('analysis'),
                                            slugify(_('Number of portuguese laws enacted yearly'))),
                           views.law_analysis_time_series, name='law_analysis_time_series'),

                       url(r'^%s$' % _('law'), views.law_list, name='law_law_list'),
                       url(r'^%s$' % _('types'), views.types_list, name='law_types_list'),
                       url(r'^%s/(\d+)$' % _('type'), views.type_view, name='law_type'),

                       url(r'^%s/(\d+)$' % _('document'), views.law_view, name='law_view'),
                       url(r'^%s/(\d+)/(.*)' % _('document'), views.law_view, name='law_view'),
                       )
