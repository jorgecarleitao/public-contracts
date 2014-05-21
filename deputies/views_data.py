import json

from django.http import HttpResponse

from .analysis import analysis_manager


def deputies_time_distribution_json(request):
    data = analysis_manager.get_analysis('deputies_time_distribution')

    for x in data:
        x['value'] = x['count']

    return HttpResponse(json.dumps(data), content_type="application/json")
