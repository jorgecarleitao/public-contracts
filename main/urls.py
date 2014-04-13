from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext as _
from django.contrib.sitemaps.views import sitemap

import contracts.urls
import deputies.urls
import law.urls
import views
from sitemaps import ContractsSitemap

sitemaps = {
    'contracts': ContractsSitemap,
}

urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^', include(contracts.urls, app_name='contracts')),
                       url(r'^', include(deputies.urls, app_name='deputies')),
                       url(r'^', include(law.urls, app_name='law')),
                       (r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),
                       (r'^robots\.txt$', views.robots),
                       )

from django.conf import settings
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
