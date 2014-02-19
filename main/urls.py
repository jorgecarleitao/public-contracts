from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext as _
from django.contrib.sitemaps.views import sitemap

import contracts.urls
import deputies.urls
import views
from sitemaps import ContractsSitemap

sitemaps = {
    'contracts': ContractsSitemap,
}

urlpatterns = patterns('',
                       url(r'^', include(contracts.urls)),
                       url(r'^%s' % _('deputies'), include(deputies.urls)),
                       (r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),
                       (r'^robots\.txt$', views.robots),
                       )

from django.conf import settings
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
