import json
import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import DateField, CharField

import requests
import requests.exceptions

from . import models
from contracts.crawler_forms import EntityForm, ContractForm, \
    TenderForm, clean_place, PriceField

logger = logging.getLogger(__name__)


class JSONLoadError(Exception):
    """
    When JSON fails to parse the content of an url.
    """
    def __init__(self, url):
        self.url = url


class JSONCrawler:
    """
    A crawler specific for retrieving JSON content.
    """
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko)'

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})

    def get_response(self, url, headers=None):

        if headers:
            self.session.headers.update(headers)

        return self.session.get(url)

    def get_json(self, url, headers=None):
        return json.loads(self.get_response(url, headers).text)


class ContractsStaticDataCrawler(JSONCrawler):
    def save_contracts_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tipocontratos'
        data = self.get_json(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, continue
                models.ContractType.objects.get(base_id=element['id'])
            except models.ContractType.DoesNotExist:
                contract_type = models.ContractType(name=element['description'],
                                                    base_id=element['id'])
                contract_type.save()

    def save_procedures_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tipoprocedimentos'
        data = self.get_json(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All that we don't use.
                continue
            try:
                # if it exists, we pass
                models.ProcedureType.objects.get(name=element['description'])
            except models.ProcedureType.DoesNotExist:
                procedure_type = models.ProcedureType(name=element['description'],
                                                      base_id=element['id'])
                procedure_type.save()

    def save_act_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tiposacto'

        data = self.get_json(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, we pass
                models.ActType.objects.get(base_id=element['id'])
            except models.ActType.DoesNotExist:
                act_type = models.ActType(name=element['description'],
                                          base_id=element['id'])
                act_type.save()

    def save_model_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tiposmodelo'
        data = self.get_json(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, we pass
                models.ModelType.objects.get(base_id=element['id'])
            except models.ModelType.DoesNotExist:
                act_type = models.ModelType(name=element['description'],
                                            base_id=element['id'])
                act_type.save()

    def save_all_countries(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/paises'
        data = self.get_json(url)

        for element in data['items']:
            try:
                # if it exists, we pass
                models.Country.objects.get(name=element['description'])
                pass
            except models.Country.DoesNotExist:
                country = models.Country(name=element['description'])
                country.save()

    def save_all_districts(self):
        base_url = 'http://www.base.gov.pt/base2/rest/lista/distritos?pais=%d'
        portugal = models.Country.objects.get(name="Portugal")

        data = self.get_json(base_url % 187)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, we pass
                models.District.objects.get(base_id=element['id'])
            except models.District.DoesNotExist:
                district = models.District(name=element['description'],
                                           base_id=element['id'],
                                           country=portugal)
                district.save()

    def save_councils(self, district):
        base_url = 'http://www.base.gov.pt/base2/rest/lista/concelhos?distrito=%d'
        data = self.get_json(base_url % district.base_id)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All", that we don't use.
                continue
            try:
                # if it exists, we pass
                models.Council.objects.get(base_id=element['id'])
            except models.Council.DoesNotExist:
                council = models.Council(name=element['description'],
                                         base_id=element['id'],
                                         district=district)
                council.save()

    def retrieve_and_save_all(self):
        self.save_contracts_types()
        self.save_procedures_types()
        self.save_model_types()
        self.save_act_types()
        # Countries first
        self.save_all_countries()
        # Districts second
        self.save_all_districts()
        # Councils third
        for district in models.District.objects.all():
            self.save_councils(district)


class DynamicCrawler(JSONCrawler):
    object_directory = '../data'
    object_url = None
    object_list_url = None
    object_name = None
    object_model = None

    def get_json(self, url, headers=None):
        """
        Raises a `JSONLoadError` if all entries are `None`,
        the BASE way of saying that the object doesn't exist in its database.
        """
        data = super(DynamicCrawler, self).get_json(url, headers)

        # ensures that data is not None
        if not isinstance(data, list) and data['id'] == 0:
            raise JSONLoadError(url)
        return data

    def get_data(self, base_id, flush=False):
        """
        Returns data retrieved from BASE or from saved file in directory

        If retrieved from BASE, saves it in a file in directory.
        """
        file_name = '%s/%s_%d.json' % (self.object_directory,
                                       self.object_name,
                                       base_id)
        try:
            if flush:
                raise IOError  # force flushing the file
            f = open(file_name, "r")
            data = json.load(f)
            f.close()
            action = 'used'
        except IOError:
            data = self.get_json(self.object_url % base_id)
            with open(file_name, 'w') as outfile:
                json.dump(data, outfile)
            action = 'created'
        logger.debug('file of %s "%d" %s', self.object_name, base_id, action)
        return data

    @staticmethod
    def clean_data(data):
        raise NotImplementedError

    def save_instance(self, cleaned_data):
        """
        Saves or updates the instance using cleaned_data
        """
        try:
            instance = self.object_model.objects.get(
                base_id=cleaned_data['base_id'])
            for (key, value) in cleaned_data.items():
                setattr(instance, key, value)
            action = 'updated'
        except self.object_model.DoesNotExist:
            instance = self.object_model(**cleaned_data)
            action = 'created'
        instance.save()
        logger.info('%s "%d" %s' % (self.object_name, cleaned_data['base_id'],
                                    action))

        return instance, (action == 'created')

    @transaction.atomic
    def update_instance(self, base_id, flush=False):
        """
        Retrieves data of object base_id from BASE,
        cleans, and saves it as an instance of a Django model.

        Returns the instance
        """
        data = self.get_data(base_id, flush)
        cleaned_data = self.clean_data(data)
        return self.save_instance(cleaned_data)

    def get_instances_count(self):
        """
        Hits BASE to get the total number of instances in BASE db.
        """
        response = self.get_response(self.object_list_url,
                                     headers={'Range': 'items=0-1'})

        results_range = response.headers['content-range']

        # in "items 0-%d/%d", we want the second %d, the total.
        return int(results_range.split('/')[1])

    def _hasher(self, instance):
        """
        Hashes a entry of BASE response to a tuple. E.g. `(instance['id'], )`.
        Add more values to better identify if the instance changed.
        """
        raise NotImplementedError

    def _values_list(self):
        """
        Returns a list of tuples that are retrieved from the database to match
        the tuple returned by `_hasher`. E.g. `('base_id',)`.
        """
        raise NotImplementedError

    def get_base_ids(self, row1, row2):

        items = self.get_json(self.object_list_url,
                              headers={'Range': 'items=%d-%d' % (row1, row2)})

        return [self._hasher(instance) for instance in items]

    def _update_batch(self, row1, row2):
        """
        Updates items from row1 to row2 of BASE db with our db.
        """
        c1s = self.get_base_ids(row1, row2)

        c2s = set(self.object_model.objects.filter(base_id__gte=c1s[0][0],
                                                   base_id__lte=c1s[-1][0])
                  .order_by('base_id').values_list(*self._values_list()))
        c1s = set(c1s)

        # just the ids
        c1_ids = set(item[0] for item in c1s)
        c2_ids = set(item[0] for item in c2s)

        aggregated_modifications = {'deleted': 0, 'added': 0, 'updated': 0}
        for item in c1s - c2s:
            id1 = item[0]
            self.update_instance(id1, flush=True)
            if id1 in c2_ids:
                aggregated_modifications['updated'] += 1
            else:
                aggregated_modifications['added'] += 1

        for id2 in c2_ids - c1_ids:
            self.object_model.objects.get(base_id=id2).delete()
            logger.info('contract "%d" deleted' % id2)
            aggregated_modifications['deleted'] += 1
        return aggregated_modifications

    def update(self, start=0, end=None, items_per_batch=1000):
        """
        The method retrieves count of all items in BASE (1 hit), and
        synchronizes items from `start` until `min(end, count)` in batches
        of `items_per_batch`.

        If `end=None` (default), it retrieves until the last item.

        if `start < 0`, the start is counted from the end.

        Use e.g. `start=-2000` for a quick retrieve of new items;

        Use `start=0` (default) to synchronize all items in database
        (it takes time!)
        """
        aggregated = {'deleted': 0, 'added': 0, 'updated': 0}

        count = self.get_instances_count()
        if end is None:
            end = count
        else:
            end = min(count, end)

        if end <= 0:
            return aggregated

        # if start < 0, start is as if it was from the maximum
        if start < 0:
            start += end
        if start > end:
            return aggregated

        # + 1 because it is [start, end]
        total_items = end - start

        # 103 // 100 = 1; we want 2 to also get the 3 in the next batch.
        batches = total_items // items_per_batch + 1

        logger.info('update of \'%s\' started: %d items in %d batches.' %
                    (self.object_name, total_items, batches))

        for i in range(batches):
            logger.info('Batch %d/%d started.' % (i + 1, batches))

            batch_aggr = self._update_batch(
                start + i*items_per_batch,
                min(end, start + (i+1)*items_per_batch))

            logger.info('Batch %d/%d finished: %s' % (i + 1, batches, batch_aggr))

            for key in aggregated:
                aggregated[key] += batch_aggr[key]

        logger.info('update of \'%s\' finished: %s' %
                    (self.object_name, aggregated))

        return aggregated


class EntitiesCrawler(DynamicCrawler):
    """
    Crawler used to retrieve entities.
    """
    object_directory = '../data/entities'
    object_url = 'http://www.base.gov.pt/base2/rest/entidades/%d'
    object_list_url = 'http://www.base.gov.pt/base2/rest/entidades'
    object_name = 'entity'
    object_model = models.Entity

    @staticmethod
    def clean_data(data):
        prepared_data = {'base_id': data['id'],
                         'name': data['description'],
                         'nif': data['nif'],
                         'country': data['location']}
        form = EntityForm(prepared_data)

        if not form.is_valid():
            logger.error('Validation of entity "%d" failed' %
                         data['id'])
            raise ValidationError(form.errors)

        return form.cleaned_data

    def _hasher(self, instance):
        return instance['id'], \
            CharField().clean(instance['nif']), \
            CharField().clean(instance['description'])

    def _values_list(self):
        return 'base_id', 'nif', 'name'


class ContractsCrawler(DynamicCrawler):
    """
    Crawler used to retrieve contracts.
    """
    object_directory = '../data/contracts'
    object_url = 'http://www.base.gov.pt/base2/rest/contratos/%d'
    object_list_url = 'http://www.base.gov.pt/base2/rest/contratos'
    object_name = 'contract'
    object_model = models.Contract

    @staticmethod
    def clean_data(data):

        places = clean_place(data['executionPlace'])
        prepared_data = {'base_id': data['id'],
                         'procedure_type': data['contractingProcedureType'],
                         'contract_type': data[u'contractTypes'],
                         'contract_description': data['objectBriefDescription'],
                         'description': data['description'],
                         'signing_date': data['signingDate'],
                         'added_date': data['publicationDate'],
                         'cpvs': data['cpvs'],
                         'category': data['cpvs'],
                         'price': data['initialContractualPrice'],
                         'country': places[0],
                         'district': places[1],
                         'council': {'district': places[1], 'council': places[2]},
                         'contractors': data['contracting'],
                         'contracted': data['contracted']
                         }

        form = ContractForm(prepared_data)

        if not form.is_valid():
            logger.error('Validation of contract "%d" failed' %
                         data['id'])
            raise ValidationError(form.errors)

        return form.cleaned_data

    def save_instance(self, cleaned_data):
        contractors = cleaned_data.pop('contractors')
        contracted = cleaned_data.pop('contracted')
        contract, created = super(ContractsCrawler, self)\
            .save_instance(cleaned_data)

        contract.contracted.clear()
        contract.contracted.add(*list(contracted))
        contract.contractors.clear()
        contract.contractors.add(*list(contractors))

        return contract, created

    def _hasher(self, instance):
        date_field = DateField(input_formats=["%d-%m-%Y"], required=False)
        return instance['id'], \
            PriceField().clean(instance['initialContractualPrice']), \
            date_field.clean(instance['signingDate'])

    def _values_list(self):
        return 'base_id', 'price', 'signing_date'


class TendersCrawler(DynamicCrawler):
    """
    Crawler used to retrieve tenders.
    """
    object_directory = '../data/tenders'
    object_url = 'http://www.base.gov.pt/base2/rest/anuncios/%d'
    object_list_url = 'http://www.base.gov.pt/base2/rest/anuncios'
    object_name = 'tender'
    object_model = models.Tender

    @staticmethod
    def clean_data(data):
        prepared_data = {'base_id': data['id'],
                         'act_type': data['type'],
                         'model_type': data['modelType'],
                         'contract_type': data['contractType'],
                         'description': data['contractDesignation'],
                         'announcement_number': data['announcementNumber'],
                         'dre_url': data['reference'],
                         'publication_date': data['drPublicationDate'],
                         'deadline_date': data['proposalDeadline'],
                         'cpvs': data['cpvs'],
                         'category': data['cpvs'],
                         'price': data['basePrice'],
                         'contractors': data['contractingEntities']}

        prepared_data['publication_date'] = \
            TenderForm.prepare_publication_date(prepared_data)
        form = TenderForm(prepared_data)

        if not form.is_valid():
            logger.error('Validation of tender "%d" failed' %
                         data['id'])
            raise ValidationError(form.errors)

        return form.cleaned_data

    def save_instance(self, cleaned_data):
        contractors = cleaned_data.pop('contractors')
        tender, created = super(TendersCrawler, self).save_instance(cleaned_data)
        tender.contractors.clear()
        tender.contractors.add(*list(contractors))

        return tender, created

    def _hasher(self, instance):
        date_field = DateField(input_formats=["%d-%m-%Y"])
        return instance['id'], \
            PriceField().clean(instance['basePrice']), \
            date_field.clean(instance['drPublicationDate'])

    def _values_list(self):
        return 'base_id', 'price', 'publication_date'
