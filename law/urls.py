from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from . import views, views_data, feed

urlpatterns = patterns('',
                       url(r'^%s/%s$' % (_('law'), _('home')), views.home, name='law_home'),
                       url(r'^%s/%s$' % (_('law'), _('analysis')), views.analysis_list, name='law_analysis'),

                       url(r'^%s/%s/(\d+)/(\w+)' % (_('law'), _('analysis')),
                           views.law_analysis, name='law_analysis_selector'),
                       url(r'^%s/%s/(\d+)' % (_('law'), _('analysis')),
                           views.law_analysis, name='law_analysis_internal_selector',
                           ),

                       url(r'^%s/%s/([-\w]+)/data' % (_('law'), _('analysis')),
                           views_data.analysis_selector, name='law_data_selector',
                           ),

                       url(r'^%s$' % _('law'), views.law_list, name='law_law_list'),
                       url(r'^%s/rss$' % _('law'), feed.LawsFeed(), name='laws_list_feed'),

                       url(r'^%s$' % _('types'), views.types_list, name='law_types_list'),

                       url(r'^%s/(\d+)$' % _('type'), views.type_view),
                       url(r'^%s/(\d+)/([-\w]+)$' % _('type'), views.type_view, name='law_type'),

                       url(r'^%s/(\d+)/rss$' % _('type'), feed.TypeDocumentsFeed()),
                       url(r'^%s/(\d+)/([-\w]+)/rss$' % _('type'), feed.TypeDocumentsFeed(),
                           name='type_documents_feed'),

                       url(r'^%s/(\d+)$' % _('document'), views.law_view, name='law_view'),
                       url(r'^%s/(\d+)/(.*)' % _('document'), views.law_view, name='law_view'),
                       )
