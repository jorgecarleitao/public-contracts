from datetime import date
from django.db.models import Count

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
        data.append(entry)

    for x in data:
        print "%s, %s" % (x['from'].year, x['count'])

    return data
