from collections import OrderedDict

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from .analysis import analysis_manager
import contracts.analysis


def analysis_selector(request, analysis_id, slug=None):
    try:
        analysis_id = int(analysis_id)
    except:
        raise Http404
    if int(analysis_id) not in contracts.analysis.PRIMARY_KEY or \
                    contracts.analysis.PRIMARY_KEY[analysis_id] not in AVAILABLE_VIEWS:
        raise Http404

    name = contracts.analysis.PRIMARY_KEY[analysis_id]

    return AVAILABLE_VIEWS[name](request)


@cache_page(60 * 60 * 24)
def entities_category_ranking(request):
    entities = analysis_manager.get_analysis('municipalities_categories_ranking')

    count = 1
    for entity in entities:
        entity.rank = count
        count += 1

    context = {'navigation_tab': 'analysis',
               'entities': entities}

    return render(request, 'contracts/analysis/entity_rank/main.html', context)


def contracts_price_histogram(request):

    data = analysis_manager.get_analysis("contracts_macro_statistics")

    context = {'navigation_tab': 'analysis',
               'count': data['total_count'],
               'price': data['total_sum']}

    return render(request,
                  'contracts/analysis/contracts_price_histogram/main.html', context)


def entities_values_histogram(request):

    context = {'navigation_tab': 'analysis'}

    return render(request,
                  'contracts/analysis/entities_values_histogram/main.html', context)


def procedure_types_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request,
                  'contracts/analysis/procedure_type_time_series/main.html', context)


@cache_page(60 * 60 * 24)
def municipalities_delta_time(request):

    entities = analysis_manager.get_analysis('municipalities_delta_time')
    count = 1
    for entity in entities:
        entity.rank = count
        count += 1

    context = {'navigation_tab': 'analysis',
               'entities': entities}

    return render(request,
                  'contracts/analysis/municipalities_delta_time/main.html', context)


def municipalities_contracts_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request,
                  'contracts/analysis/municipalities_contracts_time_series/main.html', context)


def municipalities_procedure_types_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request,
                  'contracts/analysis/municipalities_procedure_type_time_series/main.html', context)


def ministries_contracts_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request,
                  'contracts/analysis/ministries_contracts_time_series/main.html', context)


def contracts_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request, 'contracts/analysis/contracts_time_series/main.html', context)


def legislation_application_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request,
                  'contracts/analysis/legislation_application_time_series/main.html', context)


AVAILABLE_VIEWS = {
    'municipalities_delta_time': municipalities_delta_time,
    'municipalities_contracts_time_series': municipalities_contracts_time_series,
    'municipalities_procedure_types_time_series': municipalities_procedure_types_time_series,
    'municipalities_categories_ranking': entities_category_ranking,

    'ministries_contracts_time_series': ministries_contracts_time_series,
    #'ministries_delta_time': ministries_delta_time,

    'contracts_price_distribution': contracts_price_histogram,
    'entities_values_distribution': entities_values_histogram,
    'procedure_type_time_series': procedure_types_time_series,
    'contracts_time_series': contracts_time_series,
    'legislation_application_time_series': legislation_application_time_series
}


titles = OrderedDict([
        ('contracts_time_series', _('When do Portugal contract most?')),
        ('contracts_price_distribution', _('Distribution of prices of contracts')),
        ('entities_values_distribution', _('Distribution of earnings of entities')),
        ('procedure_type_time_series', _('Percentage of contracts by direct procurement or public tender')),
        ('legislation_application_time_series', _('How many contracts are published too late?')),

        ('municipalities_contracts_time_series', _('When do portuguese municipalities contract most?')),
        ('municipalities_procedure_types_time_series', _('How do portuguese municipalities contract most?')),
        ('municipalities_delta_time', _('Time of publication of municipalities')),
        ('municipalities_categories_ranking', _('Ranking of specificity of municipalities')),

        ('ministries_contracts_time_series', _('When do portuguese ministries contract most?')),
])


def analysis_list():

    analysis_list = []
    for analysis in titles:
        analysis_list.append({
            'id': contracts.analysis.ANALYSIS[analysis],
            'url': reverse('contracts_analysis_selector',
                           args=(contracts.analysis.ANALYSIS[analysis],
                                 slugify(titles[analysis]))),
            'title': titles[analysis]
        })

    return analysis_list


def analysis(request):
    return render(request, 'contracts/analysis.html', {
        'analysis': analysis_list(),
        'navigation_tab': 'analysis'})
