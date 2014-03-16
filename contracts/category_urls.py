from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import category_views
import feed

urlpatterns = patterns('',
                       url(r'(\d+)$', category_views.main_view, name='category'),
                       url(r'(\d+)/%s$' % _('contracts'), category_views.contracts, name='category_contracts'),
                       url(r'(\d+)/%s/rss$' % _('contracts'), feed.CategoryContractsFeed(), name='category_contracts_rss'),
                       url(r'(\d+)/%s$' % _('contractors'), category_views.contractors, name='category_contractors'),
                       url(r'(\d+)/%s$' % _('contracted'), category_views.contracted, name='category_contracted'),

                       url(r'(\d+)/%s$' % _('tenders'), category_views.tenders, name='category_tenders'),
                       )
