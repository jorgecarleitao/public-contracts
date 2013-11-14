# coding=utf-8
from django.db.models import Avg

from contracts import models


def get_ranking():
    return models.Entity.objects.filter(name__startswith=u'Município')\
        .annotate(avg_depth=Avg('contracts_made__category__depth'))\
        .filter(avg_depth__gt=0).order_by('-avg_depth')
