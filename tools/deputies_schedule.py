# coding=utf-8
import set_up
set_up.set_up_django_environment('settings')

from deputies import crawler, models
import contracts.models


all_entries = crawler.scrape()

for entry in all_entries:
    try:
        deputy = models.Deputy.objects.get(official_id=entry['id'])
    except models.Deputy.DoesNotExist:
        deputy = models.Deputy()

    print entry['id']
    deputy.official_id = entry['id']
    deputy.name = entry['name']
    if 'birthday' in entry:
        deputy.birthday = entry['birthday']
    else:
        deputy.birthday = None
    deputy.education = "; ".join(entry['education'])
    if 'occupation' in entry:
        deputy.occupation = "; ".join(entry['occupation'])
    else:
        deputy.occupation = ""

    if 'jobs' in entry:
        deputy.jobs = "; ".join(entry['jobs'])
    else:
        deputy.jobs = ""
    if 'current_jobs' in entry:
        deputy.current_jobs = "; ".join(entry['current_jobs'])
    else:
        deputy.current_jobs = ""
    deputy.commissions = "; ".join(entry['commissions'])
    deputy.awards = "; ".join(entry['awards'])
    deputy.save()

    for mandate_data in entry['mandates']:
        legislature = models.Legislature.objects.get(number=mandate_data['legislature'])
        party = models.Party.objects.get(abbrev=mandate_data['party'])

        # the districts have slightly different names:
        try:
            district = contracts.models.District.objects.get(name=mandate_data['constituency'])
        except contracts.models.District.DoesNotExist:
            if mandate_data['constituency'] == u"Fora da Europa" or mandate_data['constituency'] == u"Europa":
                district = None
            elif mandate_data['constituency'] == u"Madeira":
                district = contracts.models.District.objects.get(name=u"Região Autónoma da Madeira")
            elif mandate_data['constituency'] == u"Açores":
                district = contracts.models.District.objects.get(name=u"Região Autónoma dos Açores")
            else:
                raise

        try:
            mandate = models.Mandate.objects.get(deputy=deputy,
                                                 legislature=legislature,
                                                 date_begin=mandate_data['start_date'])
        except models.Mandate.DoesNotExist:
            mandate = models.Mandate()

        mandate.legislature = legislature
        mandate.party = party
        mandate.district = district
        mandate.date_begin = mandate_data['start_date']
        mandate.date_end = mandate_data['end_date'] or None
        mandate.deputy = deputy
        mandate.save()
