from django.core.cache import cache

import analysis


def get_entities_categories_ranking(flush_cache=False):
    cache_name = 'entities_categories_ranking'

    entities = cache.get(cache_name)
    if entities is None or flush_cache:
        entities = analysis.get_municipalities_specificity()
        cache.set(cache_name, entities, 60*60*48)

    return entities


def get_contracts_price_distribution(flush_cache=False):
    cache_name = 'contracts_price_distribution'

    distribution = cache.get(cache_name)
    if distribution is None or flush_cache:
        distribution = analysis.get_price_histogram()
        cache.set(cache_name, distribution, 60*60*24)

    return distribution


def get_contracts_macro_statistics(flush_cache=False):
    cache_name = 'contract_prices'

    values = cache.get(cache_name)
    if values is None or flush_cache:
        values = analysis.get_contracts_macro_statistics()
        cache.set(cache_name, values, 60*60*48)

    return values


def get_procedure_types_time_series(flush_cache=False):
    cache_name = 'procedure_type_time_series'

    values = cache.get(cache_name)
    if values is None or flush_cache:
        values = analysis.get_procedure_types_time_series()
        cache.set(cache_name, values, 60*60*24*30)  # one month

    return values


def get_municipalities_delta_time(flush_cache=False):
    cache_name = 'municipalities_delta_time'

    values = cache.get(cache_name)
    if values is None or flush_cache:
        values = analysis.get_municipalities_delta_time()
        cache.set(cache_name, values, 60*60*24)  # one day

    return values
