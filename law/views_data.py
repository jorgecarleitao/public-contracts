import json

from django.http import HttpResponse, Http404

from law.analysis import analysis_manager


def law_types_time_series_json(request):
    data = analysis_manager.get_analysis('law_types_time_series')
    return HttpResponse(json.dumps(data), content_type="application/json")


AVAILABLE_VIEWS = {
    'law-types-time-series-json': law_types_time_series_json,
    }


def analysis_selector(request, analysis_name):
    if analysis_name not in AVAILABLE_VIEWS:
        raise Http404

    return AVAILABLE_VIEWS[analysis_name](request)
