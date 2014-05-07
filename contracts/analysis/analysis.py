# coding=utf-8
from __future__ import unicode_literals

from datetime import date, timedelta
import datetime
import calendar

from django.db.models import Sum, Count
from django.db import connection

from contracts import models


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)


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


def get_entities_specificity(startswith_string):
    """
    1. We filter entities that start with "startswith_string"
    2. We compute the sum of depths and the number of contracts
    3. We exclude entities with less than 5 contracts
    4. We compute the average depth
    5. We order them by decreasing average depth
    """
    entities = models.Entity.objects \
        .filter(name__startswith=startswith_string) \
        .annotate(sum_depth=Sum('contracts_made__category__depth'), count=Count('contracts_made')) \
        .exclude(count__lt=5)

    # 4.
    entities = list(entities)
    for entity in entities:
        entity.avg_depth = entity.sum_depth*1./entity.count

    # 5.
    entities.sort(key=lambda x: x.avg_depth, reverse=True)

    return entities


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


def get_all_procedure_types_time_series():
    min_date = datetime.date(2010, 1, 1)
    end_date = datetime.date(date.today().year, date.today().month, 1)

    data = []
    for i in range(100):
        max_date = add_months(min_date, 1)
        contracts = models.Contract.objects.filter(signing_date__gte=min_date,
                                                   signing_date__lt=max_date)

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


def get_entities_delta_time(startswith_string):
    entities = models.Entity.objects.filter(name__startswith=startswith_string) \
        .annotate(total=Count('contracts_made')).exclude(total__lt=5)

    entities = list(entities)

    for entity in entities:
        count = 0
        avg = timedelta(0)
        for contract in entity.contracts_made.exclude(signing_date=None).exclude(added_date=None) \
                .values('signing_date', 'added_date'):
            avg += contract['added_date'] - contract['signing_date']
            count += 1

        entity.average_delta_time = avg.days*1./count
        entity.contracts_number = count

    entities.sort(key=lambda x: x.average_delta_time)

    return entities


def get_entities_contracts_time_series(startswith_string):
    """
    Computes the time series of number of contracts of all entities
    starting with startswith_string.
    """
    startswith_string += '%%'

    query = '''SELECT YEAR(`contracts_contract`.`signing_date`),
                       MONTH(`contracts_contract`.`signing_date`),
                       COUNT(`contracts_contract`.`id`)
                FROM `contracts_contract`
                     INNER JOIN `contracts_contract_contractors`
                         ON ( `contracts_contract`.`id` = `contracts_contract_contractors`.`contract_id` )
                     INNER JOIN `contracts_entity`
                         ON ( `contracts_contract_contractors`.`entity_id` = `contracts_entity`.`id` )
                WHERE `contracts_entity`.`name` LIKE BINARY %s
                GROUP BY YEAR(`contracts_contract`.`signing_date`), MONTH(`contracts_contract`.`signing_date`)
                '''

    cursor = connection.cursor()
    cursor.execute(query, startswith_string)

    data = []
    for row in cursor.fetchall():
        year, month, value = row
        if year is None:
            continue

        min_date = datetime.date(int(year), int(month), 1)
        max_date = add_months(min_date, 1)

        entry = {'from': min_date,
                 'to': max_date,
                 'count': int(value)}
        data.append(entry)

    return data


def get_procedure_types_time_series(startswith_string):

    min_date = datetime.date(2008, 1, 1)
    end_date = datetime.date(date.today().year, date.today().month, 1)

    data = []
    while True:
        max_date = add_months(min_date, 1)

        contracts = models.Contract.objects.filter(contractors__name__startswith=startswith_string,
                                                   signing_date__gte=min_date,
                                                   signing_date__lt=max_date)

        count = contracts.count()
        if count != 0:
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


def get_excluding_entities_contracts_time_series(startswith_string):
    """
    Computes the number of and value of contracts of all entities excluding the ones
    starting with startswith_string.
    from 2008 to today, with a window of 1 month.
    """
    min_date = datetime.date(2008, 1, 1)
    end_date = datetime.date(date.today().year, date.today().month, 1)

    entities = models.Entity.objects.exclude(name__startswith=startswith_string)

    data = []
    while True:
        max_date = add_months(min_date, 1)

        aggregate = entities.filter(contracts_made__signing_date__gte=min_date,
                                    contracts_made__signing_date__lt=max_date) \
            .aggregate(count=Count("contracts_made"), value=Sum("contracts_made__price"))

        entry = {'from': min_date,
                 'to': max_date,
                 'count': aggregate['count'],
                 'value': aggregate['value'] or 0}
        data.append(entry)
        min_date = max_date
        if min_date == end_date:
            break

    return data


def get_contracts_price_time_series():

    min_date = datetime.date(2008, 1, 1)
    end_date = datetime.date(date.today().year, date.today().month, 1)

    contracts = models.Contract.objects.all()

    data = []
    while True:
        max_date = add_months(min_date, 1)

        aggregate = contracts.filter(signing_date__gte=min_date,
                                     signing_date__lt=max_date) \
            .aggregate(count=Count("id"), value=Sum("price"))

        entry = {'from': min_date,
                 'to': max_date,
                 'count': aggregate['count'],
                 'value': aggregate['value'] or 0}
        data.append(entry)
        min_date = max_date
        if min_date == end_date:
            break

    return data


def get_legislation_application_time_series():

    max_days = 10  # Código dos contratos públicos - parte II - Contratação pública - CAPÍTULO XII - Artigo 108.

    query = '''SELECT YEAR(`contracts_contract`.`signing_date`),
                       MONTH(`contracts_contract`.`signing_date`),
                       COUNT(`contracts_contract`.`id`),
                       SUM(DATEDIFF(`contracts_contract`.`signing_date`,`contracts_contract`.`added_date`) > 10)
                FROM `contracts_contract`
                WHERE `contracts_contract`.`signing_date` IS NOT NULL
                GROUP BY YEAR(`contracts_contract`.`signing_date`), MONTH(`contracts_contract`.`signing_date`)
                '''

    cursor = connection.cursor()
    cursor.execute(query)

    data = []
    for row in cursor.fetchall():
        year, month, count, ilegal_contracts = row
        if year is None or ilegal_contracts == 0:
            continue

        min_date = datetime.date(int(year), int(month), 1)
        max_date = add_months(min_date, 1)

        entry = {'from': min_date,
                 'to': max_date,
                 'count': float(ilegal_contracts)/count}
        data.append(entry)

    return data
