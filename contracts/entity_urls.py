from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import entity_views
import feed

urlpatterns = patterns('',
                       url(r'(\d+)$', entity_views.main_view, name='entity_canonical'),
                       url(r'(\d+)/%s$' % _('contracts'), entity_views.contracts, name='entity_contracts'),
                       url(r'(\d+)/%s$' % _('costumers'), entity_views.costumers, name='entity_costumers'),
                       url(r'(\d+)/%s$' % _('tenders'), entity_views.tenders, name='entity_tenders'),
                       url(r'(\d+)/%s/rs-s$' % _('contracts'), feed.EntityFeed()),
                       url(r'(\d+)/(\w+)', entity_views.main_view, name='entity'),
                       )
