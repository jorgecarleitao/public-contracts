from datetime import date, datetime
import re

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
        documents = models.Document.laws.filter(date__year=year).order_by("-date")\
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

    min_year = 1910
    end_year = datetime.now().year - 1  # only ended years

    # exclude summaries and technical sheets
    types = models.Type.objects.exclude(id__in=[95, 97, 145, 150])

    # loop over years
    data = []
    for year in range(min_year, end_year + 1):
        min_date = date(year, 1, 1)
        max_date = date(year + 1, 1, 1)

        # annotate on all types the count of this year
        annotation = types.filter(document__date__gte=min_date,
                                  document__date__lt=max_date)\
            .annotate(count=Count("document__id"))

        # put the results in `data`, also counting the total
        # 'value' will be a dict of the form `<type_name>: <count>`
        # with an extra `'Total': <total_count>`
        entry = {'from': min_date, 'to': max_date, 'value': {}}

        total = 0
        for t in annotation:
            entry['value'][t.name] = t.count
            total += t.count
        entry['value']['Total'] = total
        data.append(entry)

    def post_processing(data):
        types_time_series = {}

        # create list of existing types (exclude "not defined" and summaries and technical sheets)
        # order by count and only use 19 types (the 20th is "Others")
        for type in models.Type.objects.exclude(id__in=[95, 97, 145, 150, 98])\
                .annotate(count=Count('document__id')).order_by('-count')[:17]:
            types_time_series[type.name] = {'values': [], 'key': type.name, 'total': 0}

        # create a special entry for "others"
        # we don't translate 'Outros' since no type is translated to English.
        others_time_series = {'values': [], 'key': 'Outros', 'total': 0}

        # populate the values from the analysis
        for entry in data:
            # append a new entry for this time-point
            for t in types_time_series:
                types_time_series[t]['values'].append(
                    {'year': entry['from'].strftime('%Y'),
                     'value': 0})
            others_time_series['values'].append(
                {'year': entry['from'].strftime('%Y'),
                 'value': 0})

            # add value to type or "others"
            for t in entry['value']:
                if t == 'Total':
                    continue

                value = entry['value'][t]
                if t in types_time_series:
                    types_time_series[t]['values'][-1]['value'] += value
                    types_time_series[t]['total'] += value
                else:
                    others_time_series['values'][-1]['value'] += value
                    others_time_series['total'] += value

        # sort them by total
        types_time_series = list(types_time_series.values())
        types_time_series = sorted(types_time_series, key=lambda x: x['total'], reverse=True)
        # and finally, insert the "Others" result in the final list
        types_time_series.append(others_time_series)
        return types_time_series

    return post_processing(data)
