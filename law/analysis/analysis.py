from collections import defaultdict
from datetime import date
import re

from django.db.models import Count
from django.db import connection

from law import models


def get_documents_time_series():

    min_year = 1910
    end_year = 2013

    contracts = models.Document.objects.all()

    data = []

    for year in range(min_year, end_year+1):
        min_date = date(year, 1, 1)
        max_date = date(year+1, 1, 1)

        aggregate = contracts.exclude(date=None).filter(date__gte=min_date,
                                                        date__lt=max_date) \
            .aggregate(count=Count("id"))

        entry = {'from': min_date,
                 'to': max_date,
                 'count': aggregate['count']}
        if aggregate['count'] > 0:
            data.append(entry)

    return data


def get_eu_impact_time_series():

    # this regex catches expressions like
    # <a href="eurlex.asp?ano=2009&id=309L0043" title="Link para Diretiva da Comunidade Europeia">2009/43/CE</a>
    # which are used to refer documents from EU.
    regex = re.compile(r'eurlex\.asp\?ano=(\d+)&amp;id=(\w+)')

    final_result = {}
    for year in range(1985, 2014):
        # we exclude types that are summaries and technical sheets
        # of the diary.
        # We also exclude documents that don't have full
        # text since we cannot tell if they mention EU laws
        # and we don't want to bias the result to any side.
        documents = models.Document.objects.filter(date__year=year).order_by("-date")\
            .exclude(text=None)

        # a dictionary of the form {id, list}
        # where id is the document id and list is a
        # list of distinct references inside the document
        results = {}
        for document in documents:
            matches = regex.findall(document.text)
            # distinct matches only:
            # we don't count references of the same law more than once
            matches = list(set(matches))

            results[document.id] = matches

        aggregate = [bool(results[doc_id]) for doc_id in results]  # "cite at least one EU law"

        final_result[year] = sum(aggregate)  # number of documents

        yield (year, final_result[year]/documents.count()*100)


def get_types_time_series():

    query = '''SELECT EXTRACT(YEAR FROM law_document.date) as s_year,
                      law_type.name,
                      COUNT(law_document.id) as doc_count
               FROM law_type
                  INNER JOIN law_document
                      ON ( law_type.id = law_document.type_id )
               WHERE NOT (law_type.dr_series = %s)
               GROUP BY s_year, law_type.name
               ORDER BY s_year, law_type.name
               '''

    cursor = connection.cursor()
    cursor.execute(query, ('II',))

    types_total = defaultdict(int)
    data = []
    current_year = 1974
    entry = None
    total = 0
    for row in cursor.fetchall():
        year, type_name, count = row
        year = int(year)

        if year != current_year:
            if entry is not None:
                entry['value']['Total'] = total
                data.append(entry)
            entry = {'from': date(year, 1, 1),
                     'to': date(year + 1, 1, 1), 'value': {}}
            current_year = year
            total = 0

        entry['value'][type_name] = count
        total += count
        types_total[type_name] += count

    return data, types_total
