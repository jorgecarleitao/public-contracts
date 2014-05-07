import json

from django.http import HttpResponse

from .analysis import AnalysisManager


def entities_category_ranking_json(request):
    data = []
    count = 0
    for entity in AnalysisManager.get_analysis('municipalities_categories_ranking'):
        count += 1
        name = entity.name.split(' ')[2:]
        name = ' '.join(name)
        data.append({'name': name, 'rank': count, 'avg_depth': entity.avg_depth})

    return HttpResponse(json.dumps(data), content_type="application/json")


def entities_category_ranking_histogram_json(request):

    entities = AnalysisManager.get_analysis('municipalities_categories_ranking')

    min_value = entities[-1].avg_depth - 0.00000001  # avoid rounding, this caused a bug before.
    max_value = entities[0].avg_depth + 0.00000001   # avoid rounding, this caused a bug before.
    n_bins = 20

    # center between max and min: min_value + (max_value - min_value)*(count)/n_bins + (max_value - min_value)/n_bins/2

    # create the histogram
    data = [{'bin': x,
             'value': 0,
             'min_position': min_value + (max_value - min_value)*x/n_bins,
             'max_position': min_value + (max_value - min_value)*(x+1)/n_bins
             } for x in range(n_bins)]

    for entity in entities:
        for x in range(n_bins):
            if data[x]['min_position'] < entity.avg_depth <= data[x]['max_position']:
                data[x]['value'] += 1
                break

    return HttpResponse(json.dumps(data), content_type="application/json")


def contracts_price_histogram_json(request):

    distribution = AnalysisManager.get_analysis('contracts_price_distribution')

    data = []
    for entry in distribution:
        if entry[1]:
            data.append({'min_position': entry[0],
                         'max_position': entry[0]*2,
                         'value': entry[1]})

    return HttpResponse(json.dumps(data), content_type="application/json")


def contracts_macro_statistics_json(request):
    data = AnalysisManager.get_analysis('contracts_macro_statistics')
    return HttpResponse(json.dumps(data), content_type="application/json")


def get_procedure_types_time_series_json(request):
    data = AnalysisManager.get_analysis('procedure_type_time_series')

    for x in data:
        x['from'] = x['from'].strftime('%Y-%m-%d')
        x['to'] = x['to'].strftime('%Y-%m-%d')

    return HttpResponse(json.dumps(data), content_type="application/json")


def municipalities_delta_time_json(request):
    data = []
    rank = 0
    for entity in AnalysisManager.get_analysis('municipalities_delta_time'):
        rank += 1
        name = entity.name.split(' ')[2:]
        name = ' '.join(name)
        data.append({'name': name, 'rank': rank, 'avg_dt': entity.average_delta_time})

    return HttpResponse(json.dumps(data), content_type="application/json")


def municipalities_delta_time_histogram_json(request):

    entities = AnalysisManager.get_analysis('municipalities_delta_time')

    min_value = entities[0].average_delta_time - 0.00000001  # avoid rounding, this caused a bug before.
    max_value = entities[-1].average_delta_time + 0.00000001   # avoid rounding, this caused a bug before.
    n_bins = 20

    # center between max and min: min_value + (max_value - min_value)*(count)/n_bins + (max_value - min_value)/n_bins/2

    # create the histogram
    data = [{'bin': x,
             'value': 0,
             'min_position': min_value + (max_value - min_value)*x/n_bins,
             'max_position': min_value + (max_value - min_value)*(x+1)/n_bins
             } for x in range(n_bins)]

    for entity in entities:
        for x in range(n_bins):
            if data[x]['min_position'] < entity.average_delta_time <= data[x]['max_position']:
                data[x]['value'] += 1
                break

    return HttpResponse(json.dumps(data), content_type="application/json")


def municipalities_contracts_time_series_json(request):
    data = AnalysisManager.get_analysis('municipalities_contracts_time_series')

    for x in data:
        x['from'] = x['from'].strftime('%Y-%m-%d')
        x['to'] = x['to'].strftime('%Y-%m-%d')

    return HttpResponse(json.dumps(data), content_type="application/json")


def municipalities_procedure_types_time_series_json(request):
    data = AnalysisManager.get_analysis('municipalities_procedure_types_time_series')

    for x in data:
        x['from'] = x['from'].strftime('%Y-%m-%d')
        x['to'] = x['to'].strftime('%Y-%m-%d')

    return HttpResponse(json.dumps(data), content_type="application/json")


def ministries_contracts_time_series_json(request):
    data = AnalysisManager.get_analysis('ministries_contracts_time_series')

    for x in data:
        x['from'] = x['from'].strftime('%Y-%m-%d')
        x['to'] = x['to'].strftime('%Y-%m-%d')

    return HttpResponse(json.dumps(data), content_type="application/json")


def excluding_municipalities_contracts_time_series_json(request):
    data = AnalysisManager.get_analysis('excluding_municipalities_contracts_time_series')

    for x in data:
        x['from'] = x['from'].strftime('%Y-%m-%d')
        x['to'] = x['to'].strftime('%Y-%m-%d')

    return HttpResponse(json.dumps(data), content_type="application/json")


def contracts_time_series_json(request):
    data = AnalysisManager.get_analysis('contracts_time_series')

    for x in data:
        x['from'] = x['from'].strftime('%Y-%m-%d')
        x['to'] = x['to'].strftime('%Y-%m-%d')

    return HttpResponse(json.dumps(data), content_type="application/json")


def legislation_application_time_series_json(request):
    data = AnalysisManager.get_analysis('legislation_application_time_series')

    for x in data:
        x['from'] = x['from'].strftime('%Y-%m-%d')
        x['to'] = x['to'].strftime('%Y-%m-%d')

    return HttpResponse(json.dumps(data), content_type="application/json")
