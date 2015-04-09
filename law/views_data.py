import json

from django.http import HttpResponse, Http404

from law.analysis import analysis_manager


def law_types_time_series_json(_):
    data, types_total = analysis_manager.get_analysis('law_types_time_series')

    total_documents = sum(types_total.values())

    types_time_series = {}
    total_presented = 0
    for type_name in sorted(types_total, key=types_total.get, reverse=True)[:17]:
        count = types_total[type_name]
        types_time_series[type_name] = {'values': [], 'key': type_name,
                                        'total': count}

        total_presented += count

    # create a special entry for "others"
    # we don't translate 'Outros' since no type is translated to English.
    others_time_series = {'values': [], 'key': 'Outros',
                          'total': total_documents - total_presented}

    # populate the values from the analysis
    for entry in data:
        # append a new entry for this time-point
        for type_name in types_time_series:
            types_time_series[type_name]['values'].append(
                {'year': entry['from'].strftime('%Y'),
                 'value': 0})
        others_time_series['values'].append(
            {'year': entry['from'].strftime('%Y'),
             'value': 0})

        # add value to type or "others"
        for type_name in entry['value']:
            if type_name == 'Total':
                continue

            value = entry['value'][type_name]
            if type_name in types_time_series:
                types_time_series[type_name]['values'][-1]['value'] += value
            else:
                others_time_series['values'][-1]['value'] += value

    # sort them by total
    types_time_series = list(types_time_series.values())
    types_time_series = sorted(types_time_series,
                               key=lambda x: x['total'], reverse=True)
    # and finally, append the "Others" in the end of the list
    types_time_series.append(others_time_series)

    return HttpResponse(json.dumps(types_time_series),
                        content_type="application/json")


AVAILABLE_VIEWS = {
    'law-types-time-series-json': law_types_time_series_json,
    }


def analysis_selector(request, analysis_name):
    if analysis_name not in AVAILABLE_VIEWS:
        raise Http404

    return AVAILABLE_VIEWS[analysis_name](request)
