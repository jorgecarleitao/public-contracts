from collections import defaultdict

from datetime import date, timedelta
import datetime
import calendar

from django.db.models import Sum, Count, F
from django.db import connection

from contracts import models


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)


def get_price_histogram():
    """
    Since the distribution is broad, we use logarithmic bins.

    For each bin, we filter contracts within these values.
    40 was arbitrarily chosen, but includes all prices.
    """
    cases = 'CASE'
    for x in range(1, 41):
        cases += ' WHEN (%d < contracts_contract.price/100 AND ' \
                 'contracts_contract.price/100 < %d) THEN %d\n' % (2**x, 2*2**x, 2**x)
    cases += ' END'

    query = """
        SELECT %s as hist, COUNT(*)
        FROM contracts_contract
        WHERE contracts_contract.price > 100
        GROUP BY hist
        ORDER BY hist ASC
    """ % cases

    cursor = connection.cursor()
    cursor.execute(query)

    data = []
    for row in cursor.fetchall():
        value, count = row
        if value is None:
            continue
        data.append([value, count])
    return data


def get_entities_value_histogram():
    """
    Returns a list of tuples (value, count_earnings, count_expenses)
    where `value` is 2^i and count_* is the number of entities with
    earnings/expenses in range [2^i, 2^(i+1)].
    We use logarithmic bins because the distribution is broad.
    """
    def _entities_histogram():
        cases_earned = 'CASE'
        for x in range(1, 43):
            cases_earned += ' WHEN (' \
                '%d < contracts_entitydata.total_earned/100 AND ' \
                'contracts_entitydata.total_earned/100 < %d) THEN %d\n' % \
                            (2**x, 2*2**x, 2**x)
        cases_earned += 'ELSE 0 END'

        cases_expended = 'CASE'
        for x in range(1, 41):
            cases_expended += ' WHEN (' \
                '%d < contracts_entitydata.total_expended/100 AND ' \
                'contracts_entitydata.total_expended/100 < %d) THEN %d\n' % \
                              (2**x, 2*2**x, 2**x)
        cases_expended += 'ELSE 0 END'

        query = """
        SELECT (%s, %s) as hist, COUNT(*)
        FROM contracts_entity
        INNER JOIN contracts_entitydata ON (contracts_entity.id =
        contracts_entitydata.entity_id)
        WHERE contracts_entitydata.total_earned > 100
        GROUP BY hist
        """ % (cases_earned, cases_expended)

        cursor = connection.cursor()
        cursor.execute(query)

        data = []
        for row in cursor.fetchall():
            value, count = row
            value = value[1:-1].split(',')
            value = [int(value[0]), int(value[1])]
            if value is None:
                continue
            data.append([value, count])
        return data

    data = _entities_histogram()
    result_earnings = defaultdict(int)
    result_expenses = defaultdict(int)
    for x in data:
        values, count = x
        result_earnings[values[0]] += count
        result_expenses[values[1]] += count

    result = []
    for x in sorted(set(result_earnings.keys()) | set(result_expenses.keys())):
        if x == 0:
            continue
        result.append((x, result_earnings[x], result_expenses[x]))

    return result


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

    # ignore procedure types with less than 100 contracts
    valid_types = models.ProcedureType.objects\
        .annotate(count=Count('contract'))\
        .exclude(count__lt=100)
    # avoid subqueries (Django related optimization)
    valid_types = list(valid_types)

    data = []
    while True:
        max_date = add_months(min_date, 1)

        # restrict to date bounds
        counts = models.ProcedureType.objects\
            .filter(id__in=[p.id for p in valid_types])\
            .filter(contract__signing_date__gte=min_date,
                    contract__signing_date__lt=max_date)

        # annotate number of contracts
        counts = counts.annotate(count=Count('contract'))

        # hit db and make it a dictionary
        counts = dict(counts.values_list('id', 'count'))

        # total of this month (to make percentages)
        total = sum([count for count in counts.values()])

        entry = {'from': min_date,
                 'to': max_date}

        for procedure_type in valid_types:
            if procedure_type.id in counts:
                entry[procedure_type.name] = counts[procedure_type.id]/total
            else:
                entry[procedure_type.name] = 0
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

    query = '''SELECT EXTRACT(YEAR FROM contracts_contract.signing_date) as s_year,
                       EXTRACT(MONTH FROM contracts_contract.signing_date) as s_month,
                       COUNT(contracts_contract.id)
                FROM contracts_contract
                     INNER JOIN contracts_contract_contractors
                         ON ( contracts_contract.id = contracts_contract_contractors.contract_id )
                     INNER JOIN contracts_entity
                         ON ( contracts_contract_contractors.entity_id = contracts_entity.id )
                WHERE contracts_entity.name ILIKE %s
                GROUP BY s_year, s_month
                ORDER BY s_year, s_month
                '''

    cursor = connection.cursor()
    cursor.execute(query, (startswith_string,))

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

    query = '''SELECT EXTRACT(YEAR FROM contracts_contract.signing_date) as s_year,
                       EXTRACT(MONTH FROM contracts_contract.signing_date) as s_month,
                       COUNT(contracts_contract.id),
                       SUM(CASE WHEN contracts_contract.signing_date - contracts_contract.added_date > 10 THEN 1 ELSE 0 END)
                FROM contracts_contract
                WHERE contracts_contract.signing_date IS NOT NULL
                GROUP BY s_year, s_month
                ORDER BY s_year, s_month
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


def get_lorenz_curve():
    # number of points in the curve. Too much degrades user performance.
    NUMBER_OF_POINTS = 500

    # all entities with earnings above 1 euro, sorted by earnings.
    entities = models.Entity.objects\
        .filter(data__total_earned__gt=F('data__total_expended'))\
        .order_by('data__total_earned')

    entities = entities.select_related('data')  # a Django-related optimization

    # compute total earnings and total number of entities
    total_earned = entities.aggregate(total=Sum('data__total_earned'))['total']
    total_count = entities.count()

    # compute and annotate the relative cumulative (entity.cumulative) and
    # relative rank (entity.rank)
    data = []
    cumulative = 0
    integral = 0
    for rank, entity in enumerate(entities):
        cumulative += entity.data.total_earned/total_earned
        entity.rank = rank/(total_count - 1)
        entity.cumulative = cumulative

        # down-sample (but always store last point)
        if rank % (total_count//NUMBER_OF_POINTS) == 0 or rank == total_count - 1:
            data.append(entity)

        integral += entity.cumulative/total_count

    return data, 1 - 2*integral  # lorenz curve, gini index
