# coding=utf-8

import datetime
from deputies import models
import contracts.models


class DeputiesDBPopulator(object):
    """
    An object that receives data from the crawler to populate the database of deputies.

    It has one entry point `populate_deputy(data)`, where data is a dictionary with content.
    """

    @staticmethod
    def _get_or_create_party(party_name):
        try:
            return models.Party.objects.get(abbrev=party_name)
        except models.Party.DoesNotExist:
            return models.Party.objects.create(abbrev=party_name)

    @staticmethod
    def _get_or_create_legislature(number, start, end):
        start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        if end == '':
            end = None
        else:
            end = datetime.datetime.strptime(end, "%Y-%m-%d").date()

        try:
            legislature = models.Legislature.objects.get(number=number)
        except models.Legislature.DoesNotExist:
            legislature = models.Legislature(number=number, date_start=start, date_end=end)

        # there must at least one deputy that stayed from the beginning
        # thus, the legislature always starts with the first existing date (within all deputies)
        # and ends in the last existing date (within all deputies).
        if legislature.date_start > start:
            legislature.date_start = start

        # the end date can be None, the case the legislature is yet to finish.
        # in this case, if end is None, we set legislature end data to None. If none of them are None,
        # we compare dates as before.
        if legislature.date_end is not None and end is not None and legislature.date_end < end or \
                                legislature.date_end is not None and end is None:
            legislature.date_end = end

        legislature.save()
        return legislature

    def populate_deputy(self, data):
        print('clean_deputy %d' % data['id']),
        try:
            deputy = models.Deputy.objects.get(official_id=data['id'])
            print 'already exists'
        except models.Deputy.DoesNotExist:
            deputy = models.Deputy()
            print 'creating entry'

        # validate data
        deputy.official_id = data['id']
        deputy.name = data['name']

        if 'birthday' in data:
            deputy.birthday = data['birthday']
        else:
            deputy.birthday = None

        deputy.save()

        for mandate_data in data['mandates']:
            legislature = self._get_or_create_legislature(mandate_data['legislature'],
                                                          mandate_data['start_date'],
                                                          mandate_data['end_date'])

            try:
                district = contracts.models.District.objects.get(name=mandate_data['constituency'])
            except contracts.models.District.DoesNotExist:
                # the districts have slightly different names
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
                                                     date_start=mandate_data['start_date'])
            except models.Mandate.DoesNotExist:
                mandate = models.Mandate()

            mandate.legislature = legislature
            mandate.party = self._get_or_create_party(mandate_data['party'])
            mandate.district = district
            mandate.date_start = mandate_data['start_date']
            mandate.date_end = mandate_data['end_date'] or None
            mandate.deputy = deputy
            mandate.save()

        return deputy
