from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from . import entity_views
from . import feed

urlpatterns = patterns('',
                       url(r'(\d+)$', entity_views.main_view, name='entity_canonical'),
                       url(r'(\d+)/%s$' % _('contracts'), entity_views.contracts, name='entity_contracts'),
                       url(r'(\d+)/%s/rss$' % _('contracts'), feed.EntityContractsFeed()),
                       url(r'(\d+)/%s/made-time-series$' % _('contracts'),
                           entity_views.contracts_made_time_series,
                           name='entity_contracts_made_time_series'),
                       url(r'(\d+)/%s/received-time-series$' % _('contracts'),
                           entity_views.contracts_received_time_series,
                           name='entity_contracts_received_time_series'),

                       url(r'(\d+)/%s$' % _('customers'), entity_views.costumers, name='entity_costumers'),

                       url(r'(\d+)/%s$' % _('tenders'), entity_views.tenders, name='entity_tenders'),
                       url(r'(\d+)/%s/rss$' % _('tenders'), feed.EntityTendersFeed()),

                       url(r'(\d+)/([-\w]+)', entity_views.main_view, name='entity'),
                       )
