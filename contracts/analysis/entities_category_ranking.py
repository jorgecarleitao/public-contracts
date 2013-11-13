# coding=utf-8
from django.core.cache import cache
from django.db.models import Avg

from contracts import models


def get_ranking():
    cache_name = 'entities_categories_ranking'

    entities = cache.get(cache_name)

    if entities is None:
        # Município = Municipality
        entities = models.Entity.objects.filter(name__startswith=u'Município') \
            .annotate(avg_depth=Avg('contracts_made__category__depth')) \
            .filter(avg_depth__gt=0).order_by('-avg_depth')
        cache.set(cache_name, list(entities), 60*60*24)

    return entities
