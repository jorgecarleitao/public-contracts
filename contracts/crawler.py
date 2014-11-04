import os
import re
import json
import logging

from django.core.exceptions import ValidationError

import requests
import requests.exceptions

from . import models
from contracts.crawler_forms import EntityForm, ContractForm, \
    TenderForm, clean_place


logger = logging.getLogger(__name__)


class EntityNotFoundError(Exception):
    def __init__(self, entities_base_ids):
        self.entities_base_ids = entities_base_ids


class JSONLoadError(Exception):
    """
    When JSON fails to parse the content of an url.
    """
    def __init__(self, url):
        self.url = url


class AbstractCrawler(object):
    """
    A thin wrapper of request.get with a custom user agent and timeout.
    """
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko)'

    def goToPage(self, url):
        response = requests.get(url, headers={'User-agent': self.user_agent},
                                timeout=10)
        return response.text


class JSONCrawler(AbstractCrawler):
    """
    A crawler specific for retrieving JSON content.
    """
    def goToPage(self, url):
        try:
            return json.loads(super(JSONCrawler, self).goToPage(url))
        except ValueError:
            raise JSONLoadError(url)
        except requests.exceptions.Timeout:
            logging.warning("timeout in url %s", url)
            raise JSONLoadError(url)


class ContractsStaticDataCrawler(JSONCrawler):
    def retrieve_and_save_contracts_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tipocontratos'
        data = self.goToPage(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, we pass
                models.ContractType.objects.get(base_id=element['id'])
                pass
            except models.ContractType.DoesNotExist:
                contract_type = models.ContractType(name=element['description'],
                                                    base_id=element['id'])
                contract_type.save()

    def retrieve_and_save_procedures_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tipoprocedimentos'
        data = self.goToPage(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All that we don't use.
                continue
            try:
                # if it exists, we pass
                models.ProcedureType.objects.get(name=element['description'])
                pass
            except models.ProcedureType.DoesNotExist:
                procedure_type = models.ProcedureType(name=element['description'],
                                                      base_id=element['id'])
                procedure_type.save()

    def retrieve_and_save_countries(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/paises'
        data = self.goToPage(url)

        for element in data['items']:
            try:
                # if it exists, we pass
                models.Country.objects.get(name=element['description'])
                pass
            except models.Country.DoesNotExist:
                country = models.Country(name=element['description'])
                country.save()

    def retrieve_and_save_districts(self):
        # We currently only retrieve from Portugal (187) because BASE only has
        # from it.
        url = 'http://www.base.gov.pt/base2/rest/lista/distritos?pais=187'
        data = self.goToPage(url)

        portugal = models.Country.objects.get(name="Portugal")

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, we pass
                models.District.objects.get(base_id=element['id'])
                pass
            except models.District.DoesNotExist:
                district = models.District(name=element['description'],
                                           base_id=element['id'],
                                           country=portugal)
                district.save()

    def retrieve_and_save_councils(self):
        base_url = 'http://www.base.gov.pt/base2/rest/lista/concelhos?distrito=%d'
        for district in models.District.objects.all():
            url = base_url % district.base_id
            data = self.goToPage(url)

            for element in data['items']:
                if element['id'] == '0':  # id = 0 is "All", that we don't use.
                    continue
                try:
                    # if it exists, we pass
                    models.Council.objects.get(base_id=element['id'])
                    pass
                except models.Council.DoesNotExist:
                    council = models.Council(name=element['description'],
                                             base_id=element['id'],
                                             district=district)
                    council.save()

    def retrieve_and_save_all(self):
        self.retrieve_and_save_contracts_types()
        self.retrieve_and_save_procedures_types()
        # Countries first
        self.retrieve_and_save_countries()
        # Districts second
        self.retrieve_and_save_districts()
        # Councils third
        self.retrieve_and_save_councils()


class TendersStaticDataCrawler(JSONCrawler):

    def retrieve_and_save_act_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tiposacto'

        data = self.goToPage(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, we pass
                models.ActType.objects.get(base_id=element['id'])
                pass
            except models.ActType.DoesNotExist:
                act_type = models.ActType(name=element['description'],
                                          base_id=element['id'])
                act_type.save()

    def retrieve_and_save_model_types(self):
        url = 'http://www.base.gov.pt/base2/rest/lista/tiposmodelo'
        data = self.goToPage(url)

        for element in data['items']:
            if element['id'] == '0':  # id = 0 is "All" that we don't use.
                continue
            try:
                # if it exists, we pass
                models.ModelType.objects.get(base_id=element['id'])
                pass
            except models.ModelType.DoesNotExist:
                act_type = models.ModelType(name=element['description'],
                                            base_id=element['id'])
                act_type.save()

    def retrieve_and_save_all(self):
        self.retrieve_and_save_model_types()
        self.retrieve_and_save_act_types()


class StaticDataCrawler():
    def __init__(self):
        self.contracts_crawler = ContractsStaticDataCrawler()
        self.tenders_crawler = TendersStaticDataCrawler()

    def retrieve_and_save_all(self):
        self.contracts_crawler.retrieve_and_save_all()
        self.tenders_crawler.retrieve_and_save_all()


class DynamicCrawler(JSONCrawler):
    object_directory = '../data'
    object_url = None
    object_name = None
    object_model = None

    MAX_ALLOWED_FAILS = 100

    def goToPage(self, url):
        """
        Raises a `JSONLoadError` if all entries are `None`,
        the BASE way of saying that the object doesn't exist in its database.
        """
        data = super(DynamicCrawler, self).goToPage(url)

        # ensures that data is not None
        if data['id'] == 0:
            raise JSONLoadError(url)
        return data

    def get_data(self, base_id, flush=False):
        """
        Returns data retrievedd from BASE or from saved file in directory

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
            data = self.goToPage(self.object_url % base_id)
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

    def update_instance(self, base_id, flush=False):
        """
        Retrieves data of object base_id from BASE,
        cleans, and saves it as an instance of a Django model.

        Returns the instance
        """
        data = self.get_data(base_id, flush)
        cleaned_data = self.clean_data(data)
        return self.save_instance(cleaned_data)

    def last_base_id(self):
        """
        Returns the last known base_id
        """
        regex = re.compile(r"%s_(\d+).json" % self.object_name)
        files = [int(re.findall(regex, f)[0])
                 for f in os.listdir('%s/' % self.object_directory)
                 if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x), reverse=True)
        if files:
            return files[0]
        else:
            return 0

    def update(self, flush=False):
        """
        Loops on all object ids to update object table.
        """
        created_instances = []

        base_id = max(self.last_base_id() - 1, 0)
        last_base_id = base_id
        fails = 0
        while True:
            base_id += 1
            try:
                instance, created = self.update_instance(base_id, flush)
                if created:
                    created_instances.append(instance)
                fails = 0
            except JSONLoadError:
                fails += 1
                if fails == self.MAX_ALLOWED_FAILS:
                    break

        logging.info("Update completed - last base_id %d", last_base_id)
        logging.info("Update completed - %d new instances",
                     len(created_instances))

        return created_instances


class EntitiesCrawler(DynamicCrawler):
    """
    Crawler used to retrieve entities.
    """
    object_directory = '../data/entities'
    object_url = 'http://www.base.gov.pt/base2/rest/entidades/%d'
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
            logging.error('Validation of entity "%d" failed' %
                          data['id'])
            raise ValidationError(form.errors)

        return form.cleaned_data


class ContractsCrawler(DynamicCrawler):
    """
    Crawler used to retrieve contracts.
    """
    object_directory = '../data/contracts'
    object_url = 'http://www.base.gov.pt/base2/rest/contratos/%d'
    object_name = 'contract'
    object_model = models.Contract

    MAX_ALLOWED_FAILS = 5000  # obtained by trial and error

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
            logging.error('Validation of contract "%d" failed' %
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


class TendersCrawler(DynamicCrawler):
    """
    Crawler used to retrieve tenders.
    """
    object_directory = '../data/tenders'
    object_url = 'http://www.base.gov.pt/base2/rest/anuncios/%d'
    object_name = 'tender'
    object_model = models.Tender

    MAX_ALLOWED_FAILS = 1000

    @staticmethod
    def clean_data(data):
        prepared_data = {'base_id': data['id'],
                         'act_type': data['type'],
                         'model_type': data['modelType'],
                         'contract_type': data['contractType'],
                         'description': data['contractDesignation'],
                         'announcement_number': data['announcementNumber'],
                         'dre_number': data['dreNumber'],
                         'dre_series': data['dreSeries'],
                         'dre_document': data['reference'],
                         'publication_date': data['drPublicationDate'],
                         'deadline_date': data['proposalDeadline'],
                         'cpvs': data['cpvs'],
                         'category': data['cpvs'],
                         'price': data['basePrice'],
                         'contractors': data['contractingEntities']}

        form = TenderForm(prepared_data)

        if not form.is_valid():
            logging.error('Validation of tender "%d" failed' %
                          data['id'])
            raise ValidationError(form.errors)

        return form.cleaned_data

    def save_instance(self, cleaned_data):
        contractors = cleaned_data.pop('contractors')
        tender, created = super(TendersCrawler, self).save_instance(cleaned_data)
        tender.contractors.clear()
        tender.contractors.add(*list(contractors))

        return tender, created


class DynamicDataCrawler():
    def __init__(self):
        self.entities_crawler = EntitiesCrawler()
        self.contracts_crawler = ContractsCrawler()
        self.tenders_crawler = TendersCrawler()

    def update_all(self):
        logger.info('Updating entities')
        modified_entities = self.entities_crawler.update()

        logger.info('Updating contracts')
        contracts = self.contracts_crawler.update()
        for contract in contracts:
            modified_entities += list(contract.contractors.all())
            modified_entities += list(contract.contracted.all())

        logger.info('Updating tenders')
        tenders = self.tenders_crawler.update()
        for tender in tenders:
            modified_entities += list(tender.contractors.all())

        def distinct(items):
            """
            Returns distinct a list of distinct elements

            see http://stackoverflow.com/a/7961390/931303
            """
            return list(set(items))

        return distinct(modified_entities)
