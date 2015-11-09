from collections import OrderedDict
import json
import string

from django.http import HttpResponse, Http404
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic import View

from .analysis import analysis_manager


def contracted_lorenz_curve(request):

    entities, gini_index = analysis_manager.get_analysis('contracted_lorenz_curve')

    data = {'values': [], 'key': _('Lorenz curve of private entities')}
    equality = {'values': [], 'key': _('Equality line')}
    for entity in entities:
        data['values'].append({'rank': entity.rank,
                               'cumulative': entity.cumulative})
        equality['values'].append({'rank': entity.rank,
                                   'cumulative': entity.rank})

    return HttpResponse(json.dumps([equality, data]),
                        content_type="application/json")


def contracts_price_histogram_json(request):
    distribution = analysis_manager.get_analysis('contracts_price_distribution')

    data = {'values': distribution, 'key': _('histogram of contracts values')}
    return HttpResponse(json.dumps([data]), content_type="application/json")


def entities_values_histogram_json(request):

    distribution = analysis_manager.get_analysis('entities_values_distribution')

    earnings = {'values': distribution[0], 'key': _('entities earning')}
    expenses = {'values': distribution[1], 'key': _('entities expending')}

    return HttpResponse(json.dumps([earnings, expenses]),
                        content_type="application/json")


class ProceduresTimeSeriesJsonView(View):
    http_method_names = ['get']
    analysis = 'procedure_type_time_series'

    def get(self, request):
        data = analysis_manager.get_analysis(self.analysis)

        series = OrderedDict()

        dates = set()  # a set of all existing dates.
        # Non-existing dates (i.e. with 0 counts) are added in the end

        for entry in data:
            procedure = entry['procedure']

            if procedure not in series:
                series[procedure] = {'values': [], 'key': procedure}

            series[procedure]['values'].append(
                {'month': entry['from'].strftime('%Y-%m'),
                 'value': entry['value'],
                 'count': entry['count']})

            dates.add(entry['from'].strftime('%Y-%m'))

        # add missing entries with 0 counts
        for procedure in series:
            for date in dates:
                if date not in [x['month'] for x in series[procedure]['values']]:
                    series[procedure]['values'].append(
                        {'month': date, 'value': 0, 'count': 0})

            series[procedure]['values'].sort(key=lambda x: x['month'])

        return HttpResponse(json.dumps(list(series.values())),
                            content_type="application/json")


class MunicipalitiesProceduresTimeSeriesJsonView(ProceduresTimeSeriesJsonView):
    analysis = 'municipalities_procedure_types_time_series'


class ContractsTimeSeriesJsonView(View):
    http_method_names = ['get']
    analysis = 'contracts_time_series'

    def get(self, request):
        data = analysis_manager.get_analysis(self.analysis)

        count_time_series = {'values': [], 'key': _('contracts'), 'bar': True}
        value_time_series = {'values': [], 'key': _('value'), 'color': 'black'}
        for x in data:
            count_time_series['values'].append(
                {'month': x['from'].strftime('%Y-%m'), 'value': x['count']})
            value_time_series['values'].append(
                {'month': x['from'].strftime('%Y-%m'), 'value': x['value']})

        return HttpResponse(json.dumps([count_time_series, value_time_series]),
                            content_type="application/json")


class MunicipalitiesTimeSeriesJsonView(ContractsTimeSeriesJsonView):
    analysis = 'municipalities_contracts_time_series'


class ExcludeMunicipalitiesTimeSeriesJsonView(ContractsTimeSeriesJsonView):
    analysis = 'excluding_municipalities_contracts_time_series'


class MinistriesTimeSeiresJsonView(ContractsTimeSeriesJsonView):
    analysis = 'ministries_contracts_time_series'


def municipalities_ranking(request):
    data = analysis_manager.get_analysis('municipalities_ranking')

    series = OrderedDict()

    # existing years and respective values for each entity.
    year_slices = {}
    # non-existing years (i.e. with 0 counts) are added in the end

    for base_id in data:
        name = string.capwords(data[base_id][0]['name'])
        series[base_id] = {'values': [], 'key': name, 'url': reverse('entity', args=(base_id, slugify(name)))}
        for entry in data[base_id]:
            year = entry['date'].strftime('%Y')

            series[base_id]['values'].append(
                {'year': year,
                 'value': entry['value'],
                 'count': entry['count'],
                 'avg_deltat': entry['avg_deltat'],
                 'avg_specificity': entry['avg_specificity'],
                 'avg_good_text': entry['avg_good_text']})

            if year not in year_slices:
                year_slices[year] = []
            year_slices[year].append({
                'base_id': base_id,
                'series_index': len(series[base_id]['values']) - 1,
                'avg_deltat': entry['avg_deltat'],
                'avg_specificity': entry['avg_specificity'],
                'avg_good_text': entry['avg_good_text']})

    # Compute the ranks for each year slice
    for year in year_slices:
        date_slice = year_slices[year]

        REVERSED_SORT = {'avg_deltat': False,
                         'avg_specificity': True,
                         'avg_good_text': True}
        for quantity in ['avg_deltat', 'avg_good_text', 'avg_specificity']:
            avg_points = [x[quantity] for x in date_slice]

            rank = 1
            previous = None
            previous_rank = 1

            for index, value in [i for i in sorted(
                    enumerate(avg_points), key=lambda x:x[1],
                    reverse=REVERSED_SORT[quantity])]:

                base_id = date_slice[index]['base_id']
                series_index = date_slice[index]['series_index']
                assert(series[base_id]['values'][series_index]['year'] == year)
                assert(series[base_id]['values'][series_index][quantity] == value)

                if value != previous:
                    previous_rank = rank
                series[base_id]['values'][series_index][quantity + '_rank'] = previous_rank

                rank += 1
                previous = value

    # add missing entries with 0 counts, typically in the current year
    for base_id in series:
        for year in year_slices:
            if year not in [x['year'] for x in series[base_id]['values']]:
                series[base_id]['values'].append(
                    {'year': year, 'value': 0, 'count': 0,
                     'avg_deltat': None,
                     'avg_deltat_rank': None,
                     'avg_specificity': None,
                     'avg_specificity_rank': None,
                     'avg_good_text': None,
                     'avg_good_text_rank': None})

        series[base_id]['values'].sort(key=lambda x: x['year'])

    return HttpResponse(json.dumps(list(series.values())),
                        content_type='application/json')


AVAILABLE_VIEWS = {
    'contracts-price-histogram-json': contracts_price_histogram_json,

    'procedure-types-time-series-json': ProceduresTimeSeriesJsonView.as_view(),

    'contracts-time-series-json': ContractsTimeSeriesJsonView.as_view(),
    'excluding-municipalities-contracts-time-series-json': ExcludeMunicipalitiesTimeSeriesJsonView.as_view(),

    'municipalities-contracts-time-series-json': MunicipalitiesTimeSeriesJsonView.as_view(),
    'municipalities-procedure-types-time-series-json': MunicipalitiesProceduresTimeSeriesJsonView.as_view(),

    'ministries-contracts-time-series-json': MinistriesTimeSeiresJsonView.as_view(),

    'entities-values-histogram-json': entities_values_histogram_json,

    'contracted-lorenz-curve-json': contracted_lorenz_curve,

    'municipalities-ranking-json': municipalities_ranking,
}


def analysis_selector(request, analysis_name):
    if analysis_name not in AVAILABLE_VIEWS:
        raise Http404

    return AVAILABLE_VIEWS[analysis_name](request)
