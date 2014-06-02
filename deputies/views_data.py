import json

from django.http import Http404, HttpResponse
from django.utils.translation import ugettext as _

from .analysis import analysis_manager


def deputies_time_distribution_json(request):
    data = analysis_manager.get_analysis('deputies_time_distribution')

    time_series = {'values': [], 'key': _('time in office')}
    for x in data:
        time_series['values'].append({'from': x['min'], 'value': x['count']})

    return HttpResponse(json.dumps([time_series]), content_type="application/json")


def mandates_distribution_json(request):
    data = analysis_manager.get_analysis('mandates_distribution')

    histogram = {'values': [], 'key': _('deputies')}
    for x in data:
        histogram['values'].append({'mandates': x['mandates'], 'value': x['count']})

    return HttpResponse(json.dumps([histogram]), content_type="application/json")


AVAILABLE_VIEWS = {
    'deputies-time-distribution-json': deputies_time_distribution_json,
    'mandates-distribution-json': mandates_distribution_json
}


def analysis_selector(request, analysis_name):
    if analysis_name not in AVAILABLE_VIEWS:
        raise Http404

    return AVAILABLE_VIEWS[analysis_name](request)
