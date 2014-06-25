import json

from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _

from .analysis import analysis_manager


def entities_category_ranking_json(request):
    data = {'values': [], 'key': _('Ranking')}
    rank = 0
    for entity in analysis_manager.get_analysis('municipalities_categories_ranking'):
        rank += 1
        name = entity.name.split(' ')[2:]
        name = ' '.join(name)
        data['values'].append({'name': name, 'rank': rank, 'avg_depth': entity.avg_depth})

    return HttpResponse(json.dumps([data]), content_type="application/json")


def entities_category_ranking_histogram_json(request):

    entities = analysis_manager.get_analysis('municipalities_categories_ranking')

    min_value = entities[-1].avg_depth - 0.00000001  # avoid rounding, this caused a bug before.
    max_value = entities[0].avg_depth + 0.00000001   # avoid rounding, this caused a bug before.
    n_bins = 20

    # center between max and min: min_value + (max_value - min_value)*(count)/n_bins + (max_value - min_value)/n_bins/2
    # create the histogram
    data = {'values': [], 'key': _('Histogram')}

    data['values'] = [{'bin': x,
                       'value': 0,
                       'min_position': min_value + (max_value - min_value)*x/n_bins,
                       'max_position': min_value + (max_value - min_value)*(x+1)/n_bins
                      } for x in range(n_bins)]

    for entity in entities:
        for x in range(n_bins):
            if data['values'][x]['min_position'] < entity.average_delta_time <= data['values'][x]['max_position']:
                data['values'][x]['value'] += 1
                break

    return HttpResponse(json.dumps([data]), content_type="application/json")


def contracts_price_histogram_json(request):

    distribution = analysis_manager.get_analysis('contracts_price_distribution')

    data = {'values': [], 'key': _('histogram of contracts values')}
    for entry in distribution:
        if entry[1] > 5:
            data['values'].append(
                {'min_position': int(entry[0] + 0.5),
                 'max_position': int(entry[0]*2 + 0.5),
                 'value': entry[1]})

    return HttpResponse(json.dumps([data]), content_type="application/json")


def entities_values_histogram_json(request):

    distribution = analysis_manager.get_analysis('entities_values_distribution')

    earnings = {'values': [], 'key': _('entities earning')}
    expenses = {'values': [], 'key': _('entities expending')}
    for entry in distribution:
        if entry[1] > 10 or entry[2] > 10:
            earnings['values'].append(
                {'min_position': int(entry[0] + 0.5),
                 'max_position': int(entry[0]*2 + 0.5),
                 'value': entry[1]})
            expenses['values'].append(
                {'min_position': int(entry[0] + 0.5),
                 'max_position': int(entry[0]*2 + 0.5),
                 'value': entry[2]})

    return HttpResponse(json.dumps([earnings, expenses]), content_type="application/json")


def contracts_macro_statistics_json(request):
    data = analysis_manager.get_analysis('contracts_macro_statistics')
    return HttpResponse(json.dumps(data), content_type="application/json")


def procedure_types_time_series_json(request):
    data = analysis_manager.get_analysis('procedure_type_time_series')

    tender_time_series = {'values': [], 'key': _('tender')}
    direct_time_series = {'values': [], 'key': _('direct procurement')}

    for x in data:
        tender_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['tender']})
        direct_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['direct']})

    return HttpResponse(json.dumps([tender_time_series, direct_time_series]), content_type="application/json")


def municipalities_delta_time_json(request):
    data = {'values': [], 'key': _('Ranking')}
    rank = 0
    for entity in analysis_manager.get_analysis('municipalities_delta_time'):
        rank += 1
        name = entity.name.split(' ')[2:]
        name = ' '.join(name)
        data['values'].append({'name': name, 'rank': rank, 'avg_dt': entity.average_delta_time})

    return HttpResponse(json.dumps([data]), content_type="application/json")


def municipalities_delta_time_histogram_json(request):

    entities = analysis_manager.get_analysis('municipalities_delta_time')

    min_value = entities[0].average_delta_time - 0.00000001  # avoid rounding, this caused a bug before.
    max_value = entities[-1].average_delta_time + 0.00000001   # avoid rounding, this caused a bug before.
    n_bins = 20

    # center between max and min: min_value + (max_value - min_value)*(count)/n_bins + (max_value - min_value)/n_bins/2

    # create the histogram
    data = {'values': [], 'key': _('Histogram')}

    data['values'] = [{'bin': x,
                       'value': 0,
                       'min_position': min_value + (max_value - min_value)*x/n_bins,
                       'max_position': min_value + (max_value - min_value)*(x+1)/n_bins
                      } for x in range(n_bins)]

    for entity in entities:
        for x in range(n_bins):
            if data['values'][x]['min_position'] < entity.average_delta_time <= data['values'][x]['max_position']:
                data['values'][x]['value'] += 1
                break

    return HttpResponse(json.dumps([data]), content_type="application/json")


def municipalities_contracts_time_series_json(request):
    data = analysis_manager.get_analysis('municipalities_contracts_time_series')

    count_time_series = {'values': [], 'key': _('contracts')}
    for x in data:
        count_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['count']})

    return HttpResponse(json.dumps([count_time_series]), content_type="application/json")


def municipalities_procedure_types_time_series_json(request):
    data = analysis_manager.get_analysis('municipalities_procedure_types_time_series')

    tender_time_series = {'values': [], 'key': _('tender')}
    direct_time_series = {'values': [], 'key': _('direct procurement')}

    for x in data:
        tender_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['tender']})
        direct_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['direct']})

    return HttpResponse(json.dumps([tender_time_series, direct_time_series]), content_type="application/json")


def ministries_contracts_time_series_json(request):
    data = analysis_manager.get_analysis('ministries_contracts_time_series')

    count_time_series = {'values': [], 'key': _('contracts')}
    for x in data:
        count_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['count']})

    return HttpResponse(json.dumps([count_time_series]), content_type="application/json")


def excluding_municipalities_contracts_time_series_json(request):
    data = analysis_manager.get_analysis('excluding_municipalities_contracts_time_series')

    count_time_series = {'values': [], 'key': _('contracts')}
    for x in data:
        count_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['count']})

    return HttpResponse(json.dumps([count_time_series]), content_type="application/json")


def contracts_time_series_json(request):
    data = analysis_manager.get_analysis('contracts_time_series')

    count_time_series = {'values': [], 'key': _('contracts')}
    for x in data:
        count_time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['count']})

    return HttpResponse(json.dumps([count_time_series]), content_type="application/json")


def legislation_application_time_series_json(request):
    data = analysis_manager.get_analysis('legislation_application_time_series')

    time_series = {'values': [], 'key': _('contracts published too late')}
    for x in data:
        time_series['values'].append({'month': x['from'].strftime('%Y-%m'), 'value': x['count']})

    return HttpResponse(json.dumps([time_series]), content_type="application/json")


AVAILABLE_VIEWS = {
    'category-ranking-index-json': entities_category_ranking_json,
    'entities-category-ranking-histogram-json': entities_category_ranking_histogram_json,
    'contracts-price-histogram-json': contracts_price_histogram_json,
    'contracts-macro-statistics-json': contracts_macro_statistics_json,

    'procedure-types-time-series-json': procedure_types_time_series_json,

    'municipalities-delta-time-json': municipalities_delta_time_json,
    'municipalities-delta-time-histogram-json': municipalities_delta_time_histogram_json,
    'contracts-time-series-json': contracts_time_series_json,
    'excluding-municipalities-contracts-time-series-json': excluding_municipalities_contracts_time_series_json,

    'municipalities-contracts-time-series-json': municipalities_contracts_time_series_json,
    'municipalities-procedure-types-time-series-json': municipalities_procedure_types_time_series_json,

    'ministries-contracts-time-series-json': ministries_contracts_time_series_json,
    'legislation-application-time-series-json': legislation_application_time_series_json,

    'entities-values-histogram-json': entities_values_histogram_json,
}


def analysis_selector(request, analysis_name):
    if analysis_name not in AVAILABLE_VIEWS:
        raise Http404

    return AVAILABLE_VIEWS[analysis_name](request)
