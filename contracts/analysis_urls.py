from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from . import views_data
from . import views_analysis


urlpatterns = patterns('',
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

                       url(r'^%s$' % _('how-many-contracts-are-published-too-late'), views_analysis.legislation_application_time_series, name='legislation_application_time_series'),
                       url(r'^%s/data$' % _('how-many-contracts-are-published-too-late'), views_data.legislation_application_time_series_json, name='legislation_application_time_series_json'),
)
