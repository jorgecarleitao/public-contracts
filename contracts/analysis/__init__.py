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
    return models.Entity.objects \
        .filter(name__startswith=u'Município') \
        .annotate(avg_depth=Avg('contracts_made__category__depth')) \
        .filter(avg_depth__gt=0) \
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


def get_procedure_types_time_series():
    import calendar
    import datetime

    def add_months(sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year,month)[1])
        return datetime.date(year, month, day)

    min_date = datetime.date(2010, 1, 1)
    end_date = datetime.date(date.today().year, date.today().month, 1)

    data = []
    for i in range(100):
        max_date = add_months(min_date, 1)
        contracts = models.Contract.objects.filter(added_date__gte=min_date,
                                                   added_date__lt=max_date)

        count = contracts.count()
        if count == 0:
            break

        entry = {'from': min_date,
                 'to': max_date,
                 'direct': contracts.filter(procedure_type_id=2).count()*1./count,
                 'tender': contracts.filter(procedure_type_id=3).count()*1./count
        }
        data.append(entry)
        min_date = max_date
        if min_date == end_date:
            break

    return data


from datetime import timedelta


def get_municipalities_delta_time():
    municipalities = models.Entity.objects.filter(name__startswith=u'Município') \
        .annotate(total=Count('contracts_made')).exclude(total__lt=5)

    municipalities = list(municipalities)

    for municipality in municipalities:
        count = 0
        avg = timedelta(0)
        for contract in municipality.contracts_made.exclude(signing_date=None).exclude(added_date=None) \
            .values('signing_date', 'added_date'):
            avg += contract['added_date'] - contract['signing_date']
            count += 1

        municipality.average_delta_time = avg.days*1./count
        municipality.contracts_number = count

    municipalities.sort(key=lambda x: x.average_delta_time)

    return municipalities
