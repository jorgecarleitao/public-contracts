from django.conf.urls import patterns, include, url

import contracts.urls
import views

urlpatterns = patterns('',
                       url(r'^', include(contracts.urls)),
                       (r'^robots\.txt$', views.robots),
                       )

from django.conf import settings
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
