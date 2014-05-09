# coding=utf-8
from __future__ import unicode_literals
import datetime
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from deputies import models
import contracts.models


class DeputiesDBPopulator(object):
    """
    An object that receives data from the crawler and populates the database of deputies.

    It has one entry point, `populate_deputy(data)`, where data is a dictionary with content
    which always updates the existing data.
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

    def _populate_mandate(self, deputy, mandate_data):
        legislature = self._get_or_create_legislature(mandate_data['legislature'],
                                                      mandate_data['start_date'],
                                                      mandate_data['end_date'])

        try:
            district = contracts.models.District.objects.get(name=mandate_data['constituency'])
        except contracts.models.District.DoesNotExist:
            # the districts have slightly different names
            if mandate_data['constituency'] == "Fora da Europa" or mandate_data['constituency'] == "Europa":
                district = None
            elif mandate_data['constituency'] == "Madeira":
                district = contracts.models.District.objects.get(name="Região Autónoma da Madeira")
            elif mandate_data['constituency'] == "Açores":
                district = contracts.models.District.objects.get(name="Região Autónoma dos Açores")
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

        return mandate

    def populate_deputy(self, data):
        try:
            deputy = models.Deputy.objects.get(official_id=data['id'])
            logger.info('clean_deputy %d already exists', data['id'])
        except models.Deputy.DoesNotExist:
            deputy = models.Deputy()
            logger.info('clean_deputy %d creating entry', data['id'])

        # validate data
        deputy.official_id = data['id']
        deputy.name = data['name']

        if 'birthday' in data:
            deputy.birthday = data['birthday']
        else:
            deputy.birthday = None

        deputy.save()

        for mandate_data in data['mandates']:
            self._populate_mandate(deputy, mandate_data)

        return deputy
