from collections import OrderedDict

from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.views.generic import View

from .analysis import analysis_manager


class CacheMixin(object):
    """
    Caches the response.
    From here: https://gist.github.com/cyberdelia/1231560
    """
    cache_timeout = 60*60*12

    def dispatch(self, *args, **kwargs):
        return cache_page(self.cache_timeout)(
            super(CacheMixin, self).dispatch)(*args, **kwargs)


class AnalysisView(CacheMixin, View):
    http_method_names = ['get']
    template_name = ''
    required_d3js = True
    nav_tab = 'analysis'

    def build_context(self, context):
        context['navigation_tab'] = 'analysis'
        context['REQUIRE_D3JS'] = self.required_d3js
        return context

    def get(self, request):
        return render(request, self.template_name, self.build_context({}))


class ContractsPriceView(AnalysisView):
    template_name = 'contracts/analysis/contracts_price_histogram/main.html'

    def build_context(self, context):
        context = super(ContractsPriceView, self).build_context(context)

        data = analysis_manager.get_analysis("contracts_statistics")
        context['count'] = data['total_count']
        context['price'] = data['total_sum']
        return context


class EntitiesValuesView(AnalysisView):
    template_name = 'contracts/analysis/entities_values_histogram/main.html'


class ProcedureTypeTimeSeriesView(AnalysisView):
    template_name = 'contracts/analysis/procedure_type_time_series/main.html'


class MunicipalitiesContractsTimeSeriesView(AnalysisView):
    template_name = 'contracts/analysis/municipalities_contracts_time_series/' \
                    'main.html'


class MunicipalitiesProceduresTimeSeriesView(AnalysisView):
    template_name = 'contracts/analysis/municipalities_procedure_type_time_' \
                    'series/main.html'


class MinistriesContractsTimeSeriesView(AnalysisView):
    template_name = 'contracts/analysis/ministries_contracts_time_series/main.html'


class MunicipalitiesRankingView(AnalysisView):
    cache_timeout = 60*60*24*30
    template_name = 'contracts/analysis/municipalities_ranking/main.html'


class ContractsTimeSeriesView(AnalysisView):
    template_name = 'contracts/analysis/contracts_time_series/main.html'


class ContractedLorenzCurveView(AnalysisView):
    template_name = 'contracts/analysis/contracted_lorenz_curve/main.html'

    def build_context(self, context):
        context = super(ContractedLorenzCurveView, self).build_context(context)

        _, gini_index = analysis_manager.get_analysis('contracted_lorenz_curve')

        context['gini_index'] = gini_index
        return context


_ANALYSIS = {
    'contracts_time_series':
        {'id': 7, 'title': _('When do Portugal contract most?'),
         'view': ContractsTimeSeriesView.as_view(), 'order': 1},
    'contracts_price_distribution':
        {'id': 9, 'title': _('Distribution of prices of contracts'),
         'view': ContractsPriceView.as_view(), 'order': 2},
    'entities_values_distribution':
        {'id': 13, 'title': _('Distribution of earnings of entities'),
         'view': EntitiesValuesView.as_view(), 'order': 3},
    'procedure_type_time_series':
        {'id': 6, 'title': _('Percentage of contracts by direct procurement '
                             'or public tender'),
         'view': ProcedureTypeTimeSeriesView.as_view(), 'order': 4},
    'municipalities_contracts_time_series':
        {'id': 2, 'title': _('When do portuguese municipalities contract most?'),
         'view': MunicipalitiesContractsTimeSeriesView.as_view(), 'order': 6},
    'municipalities_procedure_types_time_series':
        {'id': 5, 'title': _('How do portuguese municipalities contract most?'),
         'view': MunicipalitiesProceduresTimeSeriesView.as_view(), 'order': 7},
    'ministries_contracts_time_series':
        {'id': 10, 'title': _('When do portuguese ministries contract most?'),
         'view': MinistriesContractsTimeSeriesView.as_view(), 'order': 10},
    'contracted_lorenz_curve':
        {'id': 14, 'title': _('Income Inequality in Public Contracts'),
         'view': ContractedLorenzCurveView.as_view(), 'order': 11},
    'municipalities_ranking': {'id': 15, 'title': _('Municipalities Ranking'),
         'view': MunicipalitiesRankingView.as_view(), 'order': 12},
}

# order the list as `-order`
ANALYSIS = OrderedDict()
# cache id -> analysis
PRIMARY_KEY = {}
for analysis_name in sorted(_ANALYSIS, key=lambda x: _ANALYSIS[x]['order'],
                            reverse=True):
    ANALYSIS[analysis_name] = _ANALYSIS[analysis_name]

    PRIMARY_KEY[_ANALYSIS[analysis_name]['id']] = analysis_name


def analysis_selector(request, analysis_id, _):
    analysis_id = int(analysis_id)
    if analysis_id not in PRIMARY_KEY:
        return redirect('contracts_analysis')

    return ANALYSIS[PRIMARY_KEY[analysis_id]]['view'](request)


def analysis_list():

    all_analysis = []
    for name in ANALYSIS:

        identity = ANALYSIS[name]['id']
        title = ANALYSIS[name]['title']

        all_analysis.append({
            'id': identity,
            'url': reverse('contracts_analysis_selector',
                           args=(identity, slugify(title))),
            'title': title
        })

    return all_analysis


class AnalysisListView(AnalysisView):
    template_name = 'contracts/analysis.html'
    required_d3js = False

    def build_context(self, context):
        context = super(AnalysisListView, self).build_context(context)
        context['analysis'] = analysis_list()
        return context
