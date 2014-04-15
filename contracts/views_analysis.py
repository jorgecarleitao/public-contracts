from django.shortcuts import render
from django.views.decorators.cache import cache_page

from analysis import AnalysisManager


@cache_page(60 * 60 * 24)
def entities_category_ranking(request):

    entities = AnalysisManager.get_analysis('municipalities_categories_ranking')
    count = 1
    for entity in entities:
        entity.rank = count
        count += 1

    context = {'navigation_tab': 'analysis',
               'entities': entities}

    return render(request, 'contracts/entity_rank/main.html', context)


def contracts_price_histogram(request):

    data = AnalysisManager.get_analysis("contracts_macro_statistics")

    context = {'navigation_tab': 'analysis',
               'count': data['total_count'],
               'price': data['total_sum']}

    return render(request, 'contracts/contracts_price_histogram/main.html', context)


def procedure_types_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request, 'contracts/procedure_type_time_series/main.html', context)


@cache_page(60 * 60 * 24)
def municipalities_delta_time(request):

    entities = AnalysisManager.get_analysis('municipalities_delta_time')
    count = 1
    for entity in entities:
        entity.rank = count
        count += 1

    context = {'navigation_tab': 'analysis',
               'entities': entities}

    return render(request, 'contracts/municipalities_delta_time/main.html', context)


def municipalities_contracts_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request, 'contracts/municipalities_contracts_time_series/main.html', context)


def municipalities_procedure_types_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request, 'contracts/municipalities_procedure_type_time_series/main.html', context)


def ministries_contracts_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request, 'contracts/ministries_contracts_time_series/main.html', context)


def contracts_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request, 'contracts/contracts_time_series/main.html', context)

def legislation_application_time_series(request):
    context = {'navigation_tab': 'analysis'}
    return render(request, 'contracts/legislation_application_time_series/main.html', context)
