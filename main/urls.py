from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext_lazy as _
from django.contrib.sitemaps.views import sitemap

import contracts.urls
import deputies.urls
import law.urls
from . import views
from .sitemaps import Sitemap

sitemaps = {
    'sitemaps': Sitemap,
}

urlpatterns = patterns('',
                       (r'^i18n/', include('django.conf.urls.i18n')),
                       url(r'^$', views.home, name='home'),
                       url(r'^%s$' % _('about'), views.about, name='about'),
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
