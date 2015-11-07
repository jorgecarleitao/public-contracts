from collections import defaultdict

from datetime import date
import datetime
import calendar

from django.db.models import Sum, Count, F
from django.db import connection

from contracts import models


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
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
                 'contracts_contract.price/100 < %d) THEN %d\n' % (2**x, 2*2**x,
                                                                   2**x)
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


def _entities_delta_time(conditional_statement):
    """
    Annotates in a set of entities defined by a `conditional_statement`
    the average time between a contract be signed and added to the db.

    It ignores contracts before 2010 and contracts where the signing date
    or addition date is null.
    """
    query = '''
SELECT contracts_entity.id,
       contracts_entity.base_id,
       contracts_entity.name,
       AVG(contracts_contract.added_date - contracts_contract.signing_date) AS avg,
       COUNT(contracts_contract.id) AS "count"
FROM contracts_entity
  LEFT OUTER JOIN contracts_contract_contractors
    ON ( contracts_entity.id = contracts_contract_contractors.entity_id )
  LEFT OUTER JOIN contracts_contract
    ON ( contracts_contract_contractors.contract_id = contracts_contract.id )
WHERE contracts_contract.added_date IS NOT NULL AND
      contracts_contract.signing_date IS NOT NULL AND
      EXTRACT(YEAR FROM contracts_contract.signing_date) > 2009 AND
      %s
GROUP BY contracts_entity.id, contracts_entity.base_id, contracts_entity.name
ORDER BY avg ASC
    ''' % conditional_statement

    def raw_to_python(cursor):
        data = []
        for row in cursor.fetchall():
            id, base_id, name, avg, count = row
            entity = models.Entity(id=id, base_id=base_id, name=name)
            entity.average_delta_time = float(avg)
            entity.contracts_number = count
            data.append(entity)
        return data

    cursor = connection.cursor()
    cursor.execute(query)

    return raw_to_python(cursor)


def municipalities_ranking():
    """
    Computes multiple time-series of annotations of all municipalities:
    - number of contracts
    - price of contracts
    - Mean delta time
    - Mean category depth
    - Mean number of contracts with wrong/invalid descriptions

    Returns a dictionary entity_id -> time series
    """
    from pt_regions import municipalities

    NIF_TO_NAME = {}
    for m in municipalities():
        NIF_TO_NAME[str(m['NIF'])] = m['name']

    query = '''
SELECT contracts_entity.base_id, contracts_entity.nif,
  EXTRACT(YEAR FROM contracts_contract.signing_date)                   AS s_year,

  COUNT(contracts_contract.id),
  SUM(contracts_contract.price)                                        AS value,
  AVG(ABS(contracts_contract.added_date -
      contracts_contract.signing_date))                                AS avg_deltat,
  AVG(COALESCE(contracts_category.depth,
               0))                                                     AS avg_depth,
  AVG(CASE WHEN
    contracts_contract.description = contracts_contract.contract_description OR
    contracts_contract.description IS NULL OR
    contracts_contract.contract_description IS NULL
    THEN 0
      ELSE 1 END)                                                      AS count_empty_text
FROM contracts_contract
  INNER JOIN contracts_contract_contractors
    ON (contracts_contract.id = contracts_contract_contractors.contract_id)
  LEFT OUTER JOIN contracts_category
    ON (contracts_contract.category_id = contracts_category.id)
  INNER JOIN contracts_entity
    ON (contracts_contract_contractors.entity_id = contracts_entity.id)
WHERE EXTRACT(YEAR FROM contracts_contract.signing_date) > 2009 AND
      contracts_entity.nif IN (%s)
GROUP BY contracts_entity.base_id, contracts_entity.nif, s_year
HAVING COUNT(contracts_contract.id) > 0
ORDER BY contracts_entity.base_id, s_year
    ''' % ','.join(list(map(lambda x: "'%s'" % x, NIF_TO_NAME.keys())))

    def raw_to_python(cursor):
        data = {}
        for row in cursor.fetchall():
            base_id, nif, year, count, value, \
                avg_deltat, avg_specificity, avg_good_text = row
            if year is None:
                continue

            if base_id not in data:
                data[base_id] = []

            entry = {
                'name': NIF_TO_NAME[nif],
                'date': datetime.date(int(year), 1, 1),
                'count': int(count),
                'value': float(value)/100,
                'avg_deltat': float(avg_deltat),
                'avg_specificity': float(avg_specificity),
                'avg_good_text': float(avg_good_text)
            }
            data[base_id].append(entry)

        return data

    cursor = connection.cursor()
    cursor.execute(query)

    return raw_to_python(cursor)


def ministries_delta_time():
    return _entities_delta_time(
        r"contracts_entity.name ~ '^Secretaria-Geral do Ministério.*'")


def _raw_to_python(cursor):
    data = []
    for row in cursor.fetchall():
        year, month, count, value = row
        if year is None:
            continue

        min_date = datetime.date(int(year), int(month), 1)
        max_date = add_months(min_date, 1)

        entry = {'from': min_date,
                 'to': max_date,
                 'count': int(count),
                 'value': int(value/100)}
        data.append(entry)

    return data


def _entities_contracts_time_series(conditional_statement):
    distinct_query = \
        '''
SELECT DISTINCT contracts_contract.id AS id,
      contracts_contract.price AS price,
      EXTRACT(YEAR FROM contracts_contract.signing_date) AS s_year,
      EXTRACT(MONTH FROM contracts_contract.signing_date) AS s_month
FROM contracts_contract
    INNER JOIN contracts_contract_contractors
        ON ( contracts_contract.id = contracts_contract_contractors.contract_id )
    INNER JOIN contracts_entity
        ON ( contracts_contract_contractors.entity_id = contracts_entity.id )
WHERE %s
        ''' % conditional_statement

    query = '''SELECT contracts.s_year, contracts.s_month, COUNT(contracts.id), SUM(contracts.price)
               FROM (%s) AS contracts
               WHERE contracts.s_year > 2009
               GROUP BY contracts.s_year, contracts.s_month
               ORDER BY contracts.s_year, contracts.s_month
            ''' % distinct_query

    cursor = connection.cursor()
    cursor.execute(query)

    return _raw_to_python(cursor)


def municipalities_contracts_time_series():
    from pt_regions import municipalities

    return _entities_contracts_time_series(
        'contracts_entity.nif IN (%s)' %
        ','.join(["'%d'" % m['NIF'] for m in municipalities()]))


def exclude_municipalities_contracts_time_series():
    from pt_regions import municipalities

    return _entities_contracts_time_series(
        'contracts_entity.nif NOT IN (%s)' %
        ','.join(["'%d'" % m['NIF'] for m in municipalities()]))


def contracts_price_time_series():

    query = '''SELECT EXTRACT(YEAR FROM contracts_contract.signing_date) AS s_year,
       EXTRACT(MONTH FROM contracts_contract.signing_date) AS s_month,
       COUNT(contracts_contract.id),
       SUM(contracts_contract.price)
       FROM contracts_contract
       WHERE EXTRACT(YEAR FROM contracts_contract.signing_date) > 2009
       GROUP BY s_year, s_month
       ORDER BY s_year, s_month
    '''

    cursor = connection.cursor()
    cursor.execute(query)

    return _raw_to_python(cursor)


def ministries_contracts_time_series():
    return _entities_contracts_time_series(
        r"contracts_entity.name ~ '^Secretaria-Geral do Ministério.*'")


def _procedure_types_time_series_to_python(cursor):
        data = []
        for row in cursor.fetchall():
            procedure_name, year, month, count, value = row
            if year is None:
                continue

            min_date = datetime.date(int(year), int(month), 1)
            max_date = add_months(min_date, 1)

            entry = {'procedure': procedure_name,
                     'from': min_date,
                     'to': max_date,
                     'count': int(count),
                     'value': int(value/100)}

            data.append(entry)
        return data


def _entities_procedure_types_time_series(conditional_statement):

    distinct_query = '''
SELECT DISTINCT contracts_contract.id AS id,
                contracts_contract.procedure_type_id AS procedure_type,
                contracts_contract.price AS price,
                EXTRACT(YEAR FROM contracts_contract.signing_date) AS s_year,
                EXTRACT(MONTH FROM contracts_contract.signing_date) AS s_month
FROM contracts_contract
  INNER JOIN contracts_contract_contractors
    ON ( contracts_contract.id = contracts_contract_contractors.contract_id )
  INNER JOIN contracts_entity
    ON ( contracts_contract_contractors.entity_id = contracts_entity.id )
WHERE %s
''' % conditional_statement

    query = '''
SELECT contracts_proceduretype.name,
       contracts.s_year,
       contracts.s_month,
       COUNT(contracts.id),
       SUM(contracts.price)
FROM (%s) AS contracts
  INNER JOIN contracts_proceduretype
    ON ( contracts.procedure_type = contracts_proceduretype.id )
WHERE contracts.s_year > 2009
GROUP BY contracts_proceduretype.name, contracts.s_year, contracts.s_month
ORDER BY contracts_proceduretype.name, contracts.s_year, contracts.s_month
            ''' % distinct_query

    cursor = connection.cursor()
    cursor.execute(query)

    return _procedure_types_time_series_to_python(cursor)


def municipalities_procedure_types_time_series():
    from pt_regions import municipalities

    return _entities_procedure_types_time_series(
        'contracts_entity.nif IN (%s)' %
        ','.join(["'%d'" % m['NIF'] for m in municipalities()]))


def procedure_types_time_series():

    query = '''
SELECT contracts_proceduretype.name,
       EXTRACT(YEAR FROM contracts_contract.signing_date) AS s_year,
       EXTRACT(MONTH FROM contracts_contract.signing_date) AS s_month,
       COUNT(contracts_contract.id),
       SUM(contracts_contract.price)
FROM contracts_contract
  INNER JOIN contracts_proceduretype
    ON ( contracts_contract.procedure_type_id = contracts_proceduretype.id )
WHERE EXTRACT(YEAR FROM contracts_contract.signing_date) > 2009
GROUP BY contracts_proceduretype.name, s_year, s_month
ORDER BY contracts_proceduretype.name, s_year, s_month
    '''

    cursor = connection.cursor()
    cursor.execute(query)

    return _procedure_types_time_series_to_python(cursor)


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
