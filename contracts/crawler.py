from datetime import datetime, timedelta
import os
import re
import json
import logging

import requests
import requests.exceptions

from . import models

logger = logging.getLogger(__name__)


class EntityNotFoundError(Exception):
    def __init__(self, entities_base_ids):
        self.entities_base_ids = entities_base_ids


class JSONLoadError(Exception):
    """
    Error when JSON fails to parse
    an url content.
    """
    def __init__(self, url):
        self.url = url


def clean_price(item):
    """
    Transforms a string like '1.002,54 \eurochar'
    into '100254' (i.e. euro cents).
    """
    price = item.split(' ')[0]
    price = price.replace(".", "").replace(",", "")
    return int(price)


def clean_entities(items):
    """
    items is a list of dictionaries with key 'id'.
    We pick them all, or raise an IndexError if any of them doesn't exist (critical error).
    """
    ids = [item['id'] for item in items]
    entities = models.Entity.objects.filter(base_id__in=ids)

    entities_ids = [entity.base_id for entity in entities]

    # we check that all entities exist, or we raise an error.
    not_found_ids = []
    for base_id in ids:
        if base_id not in entities_ids:
            raise EntityNotFoundError(ids)
    return entities


def safe_clean_entities(items):
    """
    Cleans a list of identities base_ids
    by retrieving them from BASE if
    they are not found.
    """
    try:
        return clean_entities(items)
    except EntityNotFoundError as error:
        # in case we don't have the entity, we try to retrieve it from BASE.
        entity_crawler = EntitiesCrawler()

        entities = []
        for missing_id in error.entities_base_ids:
            # if we can't find, this raises an Error, ending the process
            entity, created = entity_crawler.update_instance(missing_id)
            entities.append(entity)
        return entities


def clean_date(string_date):
    if string_date:
        return datetime.strptime(string_date, "%d-%m-%Y").date()
    else:
        return None


def clean_deadline(string_date, string_days):
    starting_date = datetime.strptime(string_date, "%d-%m-%Y").date()

    strings = string_days.split(' ')

    if len(string_days) == 0:
        deadline = timedelta(days=0) # some don't have deadline (don't know why)
    elif strings[1] == 'dias.':
        deadline = timedelta(days=int(strings[0]))
    else:
        raise NotImplementedError

    return starting_date + deadline


def clean_cpvs(item):
    """
    It is like u'79822500-7, Servi\xe7os de concep\xe7\xe3o gr\xe1fica'
    we want u'79822500-7'
    """
    return item.split(',')[0]


def clean_category(item):
    try:
        return models.Category.objects.get(code=clean_cpvs(item))
    except models.Category.DoesNotExist:
        return None


def clean_contract_type(item):
    try:
        return models.ContractType.objects.get(name=item)
    except models.ContractType.DoesNotExist:
        return None


def clean_procedure_type(item):
    try:
        return models.ProcedureType.objects.get(name=item)
    except models.ProcedureType.DoesNotExist:
        return None


def clean_model_type(name):
    try:
        return models.ModelType.objects.get(name=name)
    except models.ModelType.DoesNotExist:
        return None


def clean_act_type(name):
    try:
        return models.ActType.objects.get(name=name)
    except models.ActType.DoesNotExist:
        return None


def clean_place(item, data):
    """
    It is like {u'executionPlace': u'Portugal, Faro, Castro Marim'}
    but it can come without council or even district.
    """
    cleaned_data = {'country': None, 'district': None, 'council': None}

    if 'executionPlace' in item and item['executionPlace']:
        names = re.split(', |<BR/>', item['executionPlace'])  # we only take the first place (they can be more than one)
        if len(names) >= 1:
            country_name = names[0]
            cleaned_data['country'] = models.Country.objects.get(name=country_name)
            if len(names) >= 2:
                district_name = names[1]
                try:
                    cleaned_data['district'] = models.District.objects.get(name=district_name, country__name=country_name)
                except models.District.DoesNotExist:
                    return data
                if len(names) >= 3:
                    council_name = names[2]
                    try:
                        cleaned_data['council'] = models.Council.objects.get(name=council_name, district__name=district_name)
                    except models.Council.DoesNotExist:
                        pass
    return cleaned_data


def clean_country(item):
    try:
        country = models.Country.objects.get(name=item)
    except IndexError:
        country = None
    except models.Country.DoesNotExist:
        country = None

    return country


def clean_dre_document(url):
    """
    we want the integer value of the last argument of the url
    """
    return int(url.split('=')[-1])


class AbstractCrawler(object):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko)'

    class NoMoreEntriesError(Exception):
        pass

    def __init__(self):
        # User-Agent. For choosing one, use for instance this with your browser: http://whatsmyuseragent.com/
        self.request_headers = {'User-agent': self.user_agent,
                                'Range': "items=0-24"}

    def goToPage(self, url):
        response = requests.get(url, headers=self.request_headers, timeout=5)
        return response.text

    def set_headers_range(self, range):
        self.request_headers['Range'] = "items=%d-%d" % range


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
                contract_type = models.ContractType(name=element['description'], base_id=element['id'])
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
                procedure_type = models.ProcedureType(name=element['description'], base_id=element['id'])
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
        url = 'http://www.base.gov.pt/base2/rest/lista/distritos?pais=187'  # 187 is Portugal.
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
                district = models.District(name=element['description'], base_id=element['id'], country=portugal)
                district.save()

    def retrieve_and_save_councils(self):
        for district in models.District.objects.all():
            url = 'http://www.base.gov.pt/base2/rest/lista/concelhos?distrito=%d' % district.base_id
            data = self.goToPage(url)

            for element in data['items']:
                if element['id'] == '0':  # id = 0 is "All", that we don't use.
                    continue
                try:
                    # if it exists, we pass
                    models.Council.objects.get(base_id=element['id'])
                    pass
                except models.Council.DoesNotExist:
                    council = models.Council(name=element['description'], base_id=element['id'], district=district)
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
                act_type = models.ActType(name=element['description'], base_id=element['id'])
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
                act_type = models.ModelType(name=element['description'], base_id=element['id'])
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
    object_directory = '../../data'
    object_url = None
    object_name = None
    object_model = None

    MAX_ALLOWED_FAILS = 100

    @staticmethod
    def block_to_range(i):
        return i*25, (i+1)*25 - 1

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

    def _save_instance(self, cleaned_data):
        """
        Saves or updates the instance using cleaned_data
        """
        try:
            instance = self.object_model.objects.get(base_id=cleaned_data['base_id'])
            for (key, value) in cleaned_data.items():
                setattr(instance, key, value)
            action = 'updated'
        except self.object_model.DoesNotExist:
            instance = self.object_model(**cleaned_data)
            action = 'created'
        instance.save()
        logger.info('%s "%d" %s' % (self.object_name, cleaned_data['base_id'], action))

        return instance, (action == 'created')

    def update_instance(self, base_id, flush=False):
        """
        Retrieves data of object base_id from BASE,
        cleans, and saves it as an instance of a Django model.

        Returns the instance
        """
        data = self.get_data(base_id, flush)
        cleaned_data = self.clean_data(data)
        entity, created = self._save_instance(cleaned_data)
        return entity, created

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

        base_id = max(self.last_base_id(), 0)
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
        logging.info("Update completed - %d new instances", len(created_instances))

        return created_instances


class EntitiesCrawler(DynamicCrawler):
    """
    Crawler used to retrieve entities.
    """
    object_directory = '../../data/entities'
    object_url = 'http://www.base.gov.pt/base2/rest/entidades/%d'
    object_name = 'entity'
    object_model = models.Entity

    @staticmethod
    def clean_data(data):
        cleaned_data = {}

        country_name = ''
        if 'location' in data:
            country_name = data['location']
        elif 'country' in data:
            country_name = data['country']

        cleaned_data['country'] = clean_country(country_name)
        cleaned_data['base_id'] = int(data['id'])
        cleaned_data['name'] = data['description']
        cleaned_data['nif'] = data['nif']

        return cleaned_data


class ContractsCrawler(DynamicCrawler):
    """
    Crawler used to retrieve contracts.
    """
    object_directory = '../../data/contracts'
    object_url = 'http://www.base.gov.pt/base2/rest/contratos/%d'
    object_name = 'contract'
    object_model = models.Contract

    @staticmethod
    def clean_data(data):

        cleaned_data = {'base_id': data['id'],
                        'procedure_type': clean_procedure_type(data['contractingProcedureType']),
                        'contract_type': clean_contract_type(data[u'contractTypes']),
                        'contract_description': data['objectBriefDescription'],
                        'description': data['description'],
                        'signing_date': clean_date(data['signingDate']),
                        'added_date': clean_date(data['publicationDate']),
                        'cpvs': clean_cpvs(data['cpvs']),
                        'category': clean_category(data['cpvs']),
                        'price': clean_price(data['initialContractualPrice'])}
        cleaned_data.update(clean_place(data, data))

        cleaned_data['contractors'] = safe_clean_entities(data['contracting'])
        cleaned_data['contracted'] = safe_clean_entities(data['contracted'])

        return cleaned_data

    def _save_instance(self, cleaned_data):
        contractors = cleaned_data.pop('contractors')
        contracted = cleaned_data.pop('contracted')
        contract, created = super(ContractsCrawler, self)._save_instance(cleaned_data)

        contract.contracted.clear()
        contract.contracted.add(*list(contracted))
        contract.contractors.clear()
        contract.contractors.add(*list(contractors))

        return contract, created


class TendersCrawler(DynamicCrawler):
    """
    Crawler used to retrieve tenders.
    """
    object_directory = '../../data/tenders'
    object_url = 'http://www.base.gov.pt/base2/rest/anuncios/%d'
    object_name = 'tender'
    object_model = models.Tender

    MAX_ALLOWED_FAILS = 1000

    @staticmethod
    def clean_data(data):

        cleaned_data = {'base_id': data['id'],
                        'act_type': clean_act_type(data['type']),
                        'model_type': clean_model_type(data['modelType']),
                        'contract_type': clean_contract_type(data['contractType']),
                        'description': data['contractDesignation'],
                        'announcement_number': data['announcementNumber'],
                        'dre_number': int(data['dreNumber']),
                        'dre_series': int(data['dreSeries']),
                        'dre_document': clean_dre_document(data['reference']),
                        'publication_date': clean_date(data['drPublicationDate']),
                        'deadline_date': clean_deadline(data['drPublicationDate'], data['proposalDeadline']),
                        'cpvs': clean_cpvs(data['cpvs']),
                        'category': clean_category(data['cpvs']),
                        'price': clean_price(data['basePrice'])}
        cleaned_data.update(clean_place(data, data))

        cleaned_data['contractors'] = safe_clean_entities(data['contractingEntities'])
        return cleaned_data


class DynamicDataCrawler():
    def __init__(self):
        self.entities_crawler = EntitiesCrawler()
        self.contracts_crawler = ContractsCrawler()
        self.tenders_crawler = TendersCrawler()

    def update_all(self):
        modified_entities = self.entities_crawler.update()

        contracts = self.contracts_crawler.update()
        for contract in contracts:
            modified_entities += list(contract.contractors.all())
            modified_entities += list(contract.contracted.all())

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
