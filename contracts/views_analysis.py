from collections import OrderedDict

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from .analysis import analysis_manager


def contracts_price_histogram(request):

    data = analysis_manager.get_analysis("contracts_macro_statistics")

    context = {'navigation_tab': 'analysis',
               'count': data['total_count'],
               'price': data['total_sum'],
               'REQUIRE_D3JS': True}

    return render(request,
                  'contracts/analysis/contracts_price_histogram/main.html',
                  context)


def entities_values_histogram(request):

    context = {'navigation_tab': 'analysis',
               'REQUIRE_D3JS': True}

    return render(request,
                  'contracts/analysis/entities_values_histogram/main.html',
                  context)


def procedure_types_time_series(request):
    context = {'navigation_tab': 'analysis',
               'REQUIRE_D3JS': True}
    return render(request,
                  'contracts/analysis/procedure_type_time_series/main.html',
                  context)


def municipalities_contracts_time_series(request):
    context = {'navigation_tab': 'analysis', 'REQUIRE_D3JS': True}
    return render(
        request,
        'contracts/analysis/municipalities_contracts_time_series/main.html',
        context)


def municipalities_procedure_types_time_series(request):
    context = {'navigation_tab': 'analysis', 'REQUIRE_D3JS': True}
    return render(
        request,
        'contracts/analysis/municipalities_procedure_type_time_series/main.html',
        context)


def ministries_contracts_time_series(request):
    context = {'navigation_tab': 'analysis', 'REQUIRE_D3JS': True}
    return render(request,
                  'contracts/analysis/ministries_contracts_time_series/main.html',
                  context)


@cache_page(60 * 60 * 24 * 30)
def municipalities_ranking(request):
    return render(request, 'contracts/analysis/municipalities_ranking/main.html',
                  {'navigation_tab': 'analysis', 'REQUIRE_D3JS': True})


def contracts_time_series(request):
    context = {'navigation_tab': 'analysis', 'REQUIRE_D3JS': True}
    return render(request, 'contracts/analysis/contracts_time_series/main.html',
                  context)


def legislation_application_time_series(request):
    context = {'navigation_tab': 'analysis', 'REQUIRE_D3JS': True}
    return render(
        request,
        'contracts/analysis/legislation_application_time_series/main.html',
        context)


def contracted_lorenz_curve(request):

    _, gini_index = analysis_manager.get_analysis('contracted_lorenz_curve')

    context = {'navigation_tab': 'analysis', 'gini_index': gini_index,
               'REQUIRE_D3JS': True}
    return render(request, 'contracts/analysis/contracted_lorenz_curve/main.html',
                  context)


_ANALYSIS = {
    'contracts_time_series':
        {'id': 7, 'title': _('When do Portugal contract most?'),
         'view': contracts_time_series, 'order': 1},
    'contracts_price_distribution':
        {'id': 9, 'title': _('Distribution of prices of contracts'),
         'view': contracts_price_histogram, 'order': 2},
    'entities_values_distribution':
        {'id': 13, 'title': _('Distribution of earnings of entities'),
         'view': entities_values_histogram, 'order': 3},
    'procedure_type_time_series':
        {'id': 6, 'title': _('Percentage of contracts by direct procurement '
                             'or public tender'),
         'view': procedure_types_time_series, 'order': 4},
    'legislation_application_time_series':
        {'id': 12, 'title': _('How many contracts are published too late?'),
         'view': legislation_application_time_series, 'order': 5},
    'municipalities_contracts_time_series':
        {'id': 2, 'title': _('When do portuguese municipalities contract most?'),
         'view': municipalities_contracts_time_series, 'order': 6},
    'municipalities_procedure_types_time_series':
        {'id': 5, 'title': _('How do portuguese municipalities contract most?'),
         'view': municipalities_procedure_types_time_series, 'order': 7},
    'ministries_contracts_time_series':
        {'id': 10, 'title': _('When do portuguese ministries contract most?'),
         'view': ministries_contracts_time_series, 'order': 10},
    'contracted_lorenz_curve':
        {'id': 14, 'title': _('Income Inequality in Public Contracts'),
         'view': contracted_lorenz_curve, 'order': 11},
    'municipalities_ranking': {'id': 15, 'title': _('Municipalities Ranking'),
         'view': municipalities_ranking, 'order': 12}
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
    try:
        analysis_id = int(analysis_id)
    except:
        raise Http404
    if int(analysis_id) not in PRIMARY_KEY:
        return redirect(analysis)

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


def analysis(request):
    return render(request, 'contracts/analysis.html', {
        'analysis': analysis_list(),
        'navigation_tab': 'analysis'})
