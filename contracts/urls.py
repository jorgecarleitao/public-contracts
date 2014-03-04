from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext as _

import feed
import views
import views_data
import views_analysis

import entity_urls
import contract_urls


urlpatterns = patterns('',
                       url(r'^$', views.home, name='contracts_home'),
                       url(r'^%s$' % _('about'), views.about, name='contracts_about'),

                       url(r'^%s$' % _('contracts'), views.contracts_list, name='contracts_list'),
                       url(r'^%s/rss$' % _('contracts'), feed.ContractsFeed(), name='contracts_list_feed'),

                       url(r'^%s$' % _('categories'), views.categories_list, name='categories_list'),
                       url(r'^%s/rss$' % _('categories'), feed.ContractsFeed()),

                       url(r'^%s$' % _('entities'), views.entities_list, name='entities_list'),

                       url(r'%s/' % _('contract'), include(contract_urls)),

                       url(r'%s/' % _('entity'), include(entity_urls)),

                       url(r'^%s/(\d+)$' % _('category'), views.category_view, name='category_view'),
                       url(r'^%s/(\d+)/rss$' % _('category'), feed.CategoryFeed(), name='category_feed'),

                       url(r'^%s$' % _('entities-category-ranking'), views_analysis.entities_category_ranking, name='entities_category_ranking'),
                       url(r'^%s/data$' % _('entities-category-ranking'), views_data.entities_category_ranking_json, name='category_ranking_index_json'),
                       url(r'^%s/data/histogram$' % _('entities-category-ranking'), views_data.entities_category_ranking_histogram_json, name='entities_category_ranking_histogram_json'),

                       url(r'^%s$' % _('contracts-price-histogram'), views_analysis.contracts_price_histogram, name='contracts_price_histogram'),
                       url(r'^%s/data$' % _('contracts-price-histogram'), views_data.contracts_price_histogram_json, name='contracts_price_histogram_json'),
                       url(r'^%s/data$' % _('contracts-macro-statistics'), views_data.contracts_macro_statistics_json, name='contracts_macro_statistics_json'),

                       url(r'^%s$' % _('procedure-type-time-series'), views_analysis.procedure_types_time_series, name='procedure_types_time_series'),
                       url(r'^%s/data$' % _('procedure-type-time-series'), views_data.get_procedure_types_time_series_json, name='procedure_types_time_series_json'),

                       url(r'^%s$' % _('municipalities-delta-time'), views_analysis.municipalities_delta_time, name='municipalities_delta_time'),
                       url(r'^%s/data$' % _('municipalities-delta-time'), views_data.municipalities_delta_time_json, name='municipalities_delta_time_json'),
                       url(r'^%s/data/histogram$' % _('municipalities-delta-time'), views_data.municipalities_delta_time_histogram_json, name='municipalities_delta_time_histogram_json'),

                       url(r'^%s$' % _('when-do-portugal-contract-most'), views_analysis.contracts_time_series, name='contracts_time_series'),
                       url(r'^%s/data$' % _('when-do-portugal-contract-most'), views_data.contracts_time_series_json, name='contracts_time_series_json'),
                       url(r'^%s/data/excluding-municipalities$' % _('when-do-portugal-contract-most'), views_data.excluding_municipalities_contracts_time_series_json, name='excluding_municipalities_contracts_time_series_json'),

                       url(r'^%s$' % _('when-do-portuguese-municipalities-contract-most'), views_analysis.municipalities_contracts_time_series, name='municipalities_contracts_time_series'),
                       url(r'^%s/data$' % _('when-do-portuguese-municipalities-contract-most'), views_data.municipalities_contracts_time_series_json, name='municipalities_contracts_time_series_json'),

                       url(r'^%s$' % _('how-do-portuguese-municipalities-contract-most'), views_analysis.municipalities_procedure_types_time_series, name='municipalities_procedure_types_time_series'),
                       url(r'^%s/data$' % _('how-do-portuguese-municipalities-contract-most'), views_data.municipalities_procedure_types_time_series_json, name='municipalities_procedure_types_time_series_json'),

                       url(r'^%s$' % _('when-do-portuguese-ministries-contract-most'), views_analysis.ministries_contracts_time_series, name='ministries_contracts_time_series'),
                       url(r'^%s/data$' % _('when-do-portuguese-ministries-contract-most'), views_data.ministries_contracts_time_series_json, name='ministries_contracts_time_series_json'),
)
