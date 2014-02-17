from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import views
import views_data


urlpatterns = patterns('',
                       url(r'^/%s$' % _('home'), views.home, name='deputies_home'),
                       url(r'^$', views.deputies, name='deputies_deputies'),
                       url(r'^/%s$' % _('parties'), views.parties, name='deputies_parties'),

                       url(r'^/%s/data$' % _('deputies-time-distribution'), views_data.deputies_time_distribution_json,
                           name='deputies_survival_distribution_json'),
)
