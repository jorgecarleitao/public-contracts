from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

from . import views
from . import views_data


urlpatterns = patterns('',
                       url(r'^%s/%s$' % (_('deputies'), _('home')), views.home, name='deputies_home'),
                       url(r'^%s' % _('deputies'), views.deputies, name='deputies_deputies'),
                       url(r'^%s$' % _('parties'), views.parties, name='deputies_parties'),
                       url(r'^%s/(\d+)$' % _('party'), views.party_view, name='party_view'),

                       url(r'^%s/data$' % _('deputies-time-distribution'), views_data.deputies_time_distribution_json,
                           name='deputies_survival_distribution_json'),
                       )
