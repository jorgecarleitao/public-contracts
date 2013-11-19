# coding=utf-8
from django.db.models import Avg, Sum, Count
from datetime import date

from contracts import models


def get_price_histogram():
    """
    Since the distribution is broad, we use logarithmic bins.

    For each bin, we filter contracts within these values.
    40 was arbitrarily chosen, but includes all prices.
    """
    data = []
    for x in range(40):
        count = models.Contract.objects.filter(price__gte=2**x, price__lt=2**(x+1)).count()
        data.append([(2**x)/100., count])  # price in euros

    return data


def get_ranking():
    """
    1. We filter entities that start with 'Município'
    2. We compute the average depth of its contracts
    3. We filter entities with average depth bigger than 0
    (Used to filter municipalities that appear twice in the official database)
    4. We order them by decreasing average depth
    """
    return models.Entity.objects\
        .filter(name__startswith=u'Município')\
        .annotate(avg_depth=Avg('contracts_made__category__depth'))\
        .filter(avg_depth__gt=0)\
        .order_by('-avg_depth')


def get_contracts_macro_statistics():
    contracts = models.Contract.objects.all()

    today = date.today()
    contracts_year = contracts.filter(signing_date__year=today.year)
    contracts_month = contracts_year.filter(signing_date__month=today.month)

    total_price = contracts.aggregate(count=Count('price'), sum=Sum('price'))
    year_price = contracts_year.aggregate(count=Count('price'), sum=Sum('price'))
    month_price = contracts_month.aggregate(count=Count('price'), sum=Sum('price'))

    return {'total_sum': total_price['sum'],
            'total_count': total_price['count'],
            'year_sum': year_price['sum'],
            'year_count': year_price['count'],
            'month_sum': month_price['sum'],
            'month_count': month_price['count']}
