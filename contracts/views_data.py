import json
from django.http import HttpResponse
import analysis.entities_category_ranking
from django.core.cache import cache


def get_entities_categories_ranking():
    cache_name = 'entities_categories_ranking'

    entities = cache.get(cache_name)
    if entities is None:
        entities = analysis.entities_category_ranking.get_ranking()
        cache.set(cache_name, list(entities), 60*60*24)

    return entities


def entities_category_ranking_json(request):


    data = []
    count = 0
    for entity in get_entities_categories_ranking():
        count += 1
        name = entity.name.split(' ')[2:]
        name = ' '.join(name)
        data.append({'name': name, 'rank': count, 'avg_depth': entity.avg_depth})

    return HttpResponse(json.dumps(data), content_type="application/json")


def entities_category_ranking_histogram_json(request):

    entities = get_entities_categories_ranking()

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
