from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import entity_views
import feed

urlpatterns = patterns('',
                       url(r'(\d+)/rss$', feed.EntityFeed(), name='entity_view'),
                       url(r'(\d+)$', entity_views.main_view, name='entity_canonical'),
                       url(r'(\d+)/%s$' % _('contracts'), entity_views.contracts, name='entity_contracts'),
                       url(r'(\d+)/(\w+)', entity_views.main_view, name='entity'),
                       )
