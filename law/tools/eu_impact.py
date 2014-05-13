## setup the Django with public settings for using the database.
if __name__ == "__main__":
    from . import set_up
    set_up.set_up_django_environment('law.tools.settings_public')

import re

from law.models import Document


def compute_time_series():

    # this regex catches expressions of the form
    # <a href="eurlex.asp?ano=2009&id=309L0043" title="Link para Diretiva da Comunidade Europeia">2009/43/CE</a>
    # which are used to refer documents from EU.
    regex = re.compile(r'eurlex\.asp\?ano=(\d+)&amp;id=(\w+)')

    final_result = {}
    for year in range(1985, 2014):
        # we exclude types that are summaries of the Diary and technical sheets (they are part of the Diary, but are
        # more like tables of contents).
        # we also exclude documents that don't have full text since we cannot tell if they mention EU laws.
        documents = Document.objects.filter(date__year=year).order_by("-date")\
            .exclude(type_id__in=[95, 97, 145, 150])\
            .exclude(text=None)

        results = {}
        for document in documents:
            matches = regex.findall(document.text)
            # distinct matches only
            matches = list(set(matches))

            results[document.id] = matches

        aggregate = [bool(results[id]) for id in results]

        final_result[year] = sum(aggregate)

        yield (year, final_result[year]/documents.count()*100)


# from public-contracts/law directory, run `python -m tools.eu_impact > s.dat`
if __name__ == "__main__":
    for year, percentage in compute_time_series():
        print("%d %f" % (year, percentage))
