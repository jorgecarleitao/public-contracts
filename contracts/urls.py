from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import views
import views_data


urlpatterns = patterns('',
                       url(r'^$', views.home, name='contracts_home'),
                       url(r'^%s$' % _('about'), views.about, name='contracts_about'),
                       url(r'^%s$' % _('contracts'), views.contracts_list, name='contracts_list'),
                       url(r'^%s$' % _('categories'), views.categories_list, name='categories_list'),
                       url(r'^%s$' % _('entities'), views.entities_list, name='entities_list'),

                       url(r'^%s/(\d+)$' % _('category'), views.category_view, name='category_view'),

                       url(r'^%s$' % _('entities-category-ranking'), views.entities_category_ranking, name='entities_category_ranking'),
                       url(r'^%s/data$' % _('entities-category-ranking'), views_data.entities_category_ranking_json, name='category_ranking_index_json'),
                       url(r'^%s/data/histogram$' % _('entities-category-ranking'), views_data.entities_category_ranking_histogram_json, name='entities_category_ranking_histogram_json'),

                       url(r'^%s$' % _('contracts-price-histogram'), views.contracts_price_histogram, name='contracts_price_histogram'),
                       url(r'^%s/data$' % _('contracts-price-histogram'), views_data.contracts_price_histogram_json, name='contracts_price_histogram_json')
                       )
