from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _

from . import feed
from . import views
from . import views_analysis
from . import views_data

from . import entity_urls
from . import contract_urls
from . import category_urls


urlpatterns = patterns(
    '',
    url(r'^%s/%s$' % (_('contracts'), _('home')),
        views.home, name='contracts_home'),

    url(r'^%s/%s$' % (_('contracts'), _('analysis')),
        views_analysis.analysis, name='contracts_analysis'),

    url(r'^%s/%s/(\d+)/(\w+)' % (_('contracts'), _('analysis')),
        views_analysis.analysis_selector,
        name='contracts_analysis_selector'),
    url(r'^%s/%s/(\d+)' % (_('contracts'), _('analysis')),
        views_analysis.analysis_selector,
        name='contracts_internal_analysis_selector',
        ),

    url(r'^%s/%s/([-\w]+)/data' % (_('contracts'), _('analysis')),
        views_data.analysis_selector,
        name='contracts_data_selector',
        ),

    url(r'%s/' % _('contract'), include(contract_urls)),
    url(r'%s/' % _('entity'), include(entity_urls)),
    url(r'%s/' % _('category'), include(category_urls)),
)

# lists
urlpatterns += patterns(
    '',
    url(r'^%s$' % _('contracts'), views.contracts_list, name='contracts_list'),
    url(r'^%s/rss$' % _('contracts'), feed.ContractsFeed(),
        name='contracts_list_feed'),

    url(r'^%s$' % _('categories'), views.categories_list,
        name='categories_list'),

    url(r'^%s$' % _('tenders'), views.tenders_list, name='tenders_list'),
    url(r'^%s/rss$' % _('tenders'), feed.TendersFeed(),
        name='tenders_list_feed'),

    url(r'^%s$' % _('entities'), views.entities_list, name='entities_list'),
)
