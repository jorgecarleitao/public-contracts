from datetime import datetime, timedelta
import os
import pickle
import re
import json
from urllib.error import HTTPError
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

import requests

from . import models


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
    data['country'] = None
    data['district'] = None
    data['council'] = None
    if 'executionPlace' in item and item['executionPlace']:
        names = re.split(', |<BR/>', item['executionPlace'])  # we only take the first place (they can be more than one)
        if len(names) >= 1:
            country_name = names[0]
            data['country'] = models.Country.objects.get(name=country_name)
            if len(names) >= 2:
                district_name = names[1]
                try:
                    data['district'] = models.District.objects.get(name=district_name, country__name=country_name)
                except models.District.DoesNotExist:
                    return data
                if len(names) >= 3:
                    council_name = names[2]
                    try:
                        data['council'] = models.Council.objects.get(name=council_name, district__name=district_name)
                    except models.Council.DoesNotExist:
                        return data
    return data


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
        response = requests.get(url, headers=self.request_headers)
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
    data_directory = '../../data'

    @staticmethod
    def block_to_range(i):
        return i*25, (i+1)*25 - 1


class EntitiesCrawler(DynamicCrawler):
    """
    A crawler to be used daily to retrieve new entities.
    """
    entities_directory = '../../data/entities'

    def get_entity_data(self, base_id, flush=False):
        """
        Returns the raw data of an entity from BASE.
        """
        file_name = '%s/entity_%d.json' % (self.entities_directory, base_id)
        try:
            if flush:
                raise IOError  # force flushing the file
            f = open(file_name, "r")
            data = json.load(f)
            f.close()
            action = 'used'
        except IOError:
            data = self.goToPage("http://www.base.gov.pt/base2/rest/entidades/%d" % base_id)
            with open(file_name, 'w') as outfile:
                json.dump(data, outfile)
            action = 'created'
        logger.debug('file of entity "%d" %s', base_id, action)
        return data

    @staticmethod
    def clean_entity_data(data):
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

    @staticmethod
    def save_entity(cleaned_data):
        """
        Saves or updates an entity using the cleaned_data
        """
        try:
            entity = models.Entity.objects.get(base_id=cleaned_data['base_id'])
            for (key, value) in cleaned_data.items():
                setattr(entity, key, value)
            action = 'updated'
        except models.Entity.DoesNotExist:
            entity = models.Entity(**cleaned_data)
            action = 'created'
        entity.save()
        logger.info('entity "%d" %s' % (cleaned_data['base_id'], action))

        return entity, action == 'created'

    def update_entity(self, base_id, flush=False):
        """
        Retrieves data of entity base_id from BASE,
        cleans, and saves it as an entity.

        Returns the entity
        """
        data = self.get_entity_data(base_id, flush)
        cleaned_data = self.clean_entity_data(data)
        entity = self.save_entity(cleaned_data)
        return entity

    def update(self, flush=False):
        """
        Loops on all entities ids to create or
        update entities table.
        """
        created_entities = []

        MAX_ALLOWED_FAILS = 100

        base_id = self.last_base_id() - MAX_ALLOWED_FAILS
        last_base_id = base_id
        fails = 0
        while True:
            base_id += 1
            try:
                entity, created = self.update_entity(base_id, flush)
                if created:
                    created_entities.append(entity)
                fails = 0
            except JSONLoadError:
                fails += 1
                if fails == MAX_ALLOWED_FAILS:
                    break

        logging.info("Update completed - last base_id %d", last_base_id)
        logging.info("Update completed - %d new entities", len(created_entities))

        return created_entities

    def last_base_id(self):
        regex = re.compile(r"entity_(\d+).json")
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s/' % self.entities_directory) if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x), reverse=True)
        if files:
            return files[0]
        else:
            return 0


class ContractsCrawler(DynamicCrawler):
    """
    A crawler to be used daily to retrieve new contracts.
    """
    contracts_directory = '../../contracts'

    def _last_contract_block(self):
        """
        Returns the last block existent in the database
        This is computed using the files we saved. The regex expression must be compatible to the
        name given in `_get_contracts_block`.
        """
        regex = re.compile(r"(\d+).dat")
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s/' % self.data_directory) if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x), reverse=True)
        if len(files):
            return files[0]
        else:
            return 0

    def _get_contracts_block(self, block):
        """
        Returns a block of 25 contracts from a file.
        If the file doesn't exist or returns less than 25 contracts,
        it hits Base's database and updates the file.

        It raises a `NoMoreEntriesError` if the retrieval returned 0 contracts i.e. if we have reached
        the last existing contract in Base's database.
        """
        def _retrieve_contracts():
            self.set_headers_range(self.block_to_range(block))
            data = self.goToPage("http://www.base.gov.pt/base2/rest/contratos")
            if len(data) == 0:  # if there are no entries, we just stop the procedure.
                raise self.NoMoreEntriesError
            return data

        file_name = '%s/%d.dat' % (self.data_directory, block)
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            if len(data) != 25:  # if block is not complete, we retrieve it again to complete it.
                logger.info('_get_contracts_block(%d) returns len(data) = %d != 25', block, len(data))
                raise IOError
            f.close()
        except IOError:
            # online retrieval
            data = _retrieve_contracts()

            f = open(file_name, "wb")
            pickle.dump(data, f)
            f.close()
        return data

    def _retrieve_and_save_contract_data(self, base_id):
        """
        Returns the data of a contract. It first tries the file. If the file doesn't exist,
        it retrieves the data from BASE and saves it in the file.
        """

        def _retrieve_contract_data():
            """
            Retrieves data from a specific contract.
            """
            logger.info('_retrieve_contract(%d)', base_id)
            url = 'http://www.base.gov.pt/base2/rest/contratos/%d' % base_id
            return self.goToPage(url)

        file_name = '%s/%d.dat' % (self.contracts_directory, base_id)
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            f.close()
        except IOError:
            # online retrieval
            data = _retrieve_contract_data()
            f = open(file_name, "wb")
            pickle.dump(data, f)
            f.close()
        return data

    def _save_contract(self, item):
        data = {'base_id': item['id'],
                'procedure_type': clean_procedure_type(item['contractingProcedureType']),
                'contract_type': clean_contract_type(item[u'contractTypes']),
                'contract_description': item['objectBriefDescription'],
                'description': item['description'],
                'signing_date': clean_date(item['signingDate']),
                'added_date': clean_date(item['publicationDate']),
                'cpvs': clean_cpvs(item['cpvs']),
                'price': clean_price(item['initialContractualPrice'])}
        data = clean_place(item, data)

        # we try to associate the cpvs to a category
        try:
            data['category'] = models.Category.objects.get(code=data['cpvs'])
        except models.Category.DoesNotExist:
            data['category'] = None

        # we try to see if it already exists
        try:
            contract = models.Contract.objects.get(base_id=data['base_id'])
            logger.info('_save_contract(%s): contract %d already exists', item['id'], data['base_id'])
        except models.Contract.DoesNotExist:
            # if it doesn't exist, we create it
            contract = models.Contract.objects.create(**data)
            logger.info('_save_contract(%s): contract %d saved', item['id'], data['base_id'])

        contractors = self._safe_clean_entities(item['contracting'])
        contracted = self._safe_clean_entities(item['contracted'])
        contract.contracted.add(*list(contracted))
        contract.contractors.add(*list(contractors))

        return list(contracted) + list(contractors)

    def _save_contracts(self, block):
        logger.info('save_contracts(%d)', block)
        raw_contracts = self._get_contracts_block(block)

        affected_entities = []
        for raw_contract in raw_contracts:
            try:
                data = self._retrieve_and_save_contract_data(raw_contract['id'])
                affected_entities += self._save_contract(data)
            # this has given errors before, we log the contract number to gain some information.
            except:
                logger.exception('error on saving contract %d', raw_contract['id'])
                raise

        return affected_entities

    def update(self):
        modified_entities = []

        block = self._last_contract_block()
        while True:
            try:
                modified_entities += self._save_contracts(block)
                block += 1
            except self.NoMoreEntriesError:
                break

        return modified_entities

    @staticmethod
    def _safe_clean_entities(items):
        try:
            return clean_entities(items)
        except EntityNotFoundError as error:
            # in case we don't have the entity, we try to retrieve it from BASE.
            entity_crawler = EntitiesCrawler()

            entities = []
            for missing_id in error.entities_base_ids:
                entity = entity_crawler.update_entity(missing_id)
                entities.append(entity)
            return entities


class TendersCrawler(DynamicCrawler):
    """
    A crawler to be used daily to retrieve new tenders.
    """
    tenders_directory = '../../tenders'

    def _last_base_id(self):
        """
        Returns the last existent item in the database
        This is computed using the files we saved. The regex expression must be compatible to the
        name given in `_retrieve_and_save_tender_data`.
        """
        regex = re.compile(r"(\d+).dat")
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s/' % self.tenders_directory) if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x), reverse=True)
        if len(files):
            return files[0]
        else:
            return 1

    def _retrieve_and_cache_tender_data(self, base_id):
        """
        Returns the data of a tender. It first tries the file. If the file doesn't exist,
        it retrieves the data from Base and saves it in the file.
        """
        def _retrieve_tender_data():
            """
            Retrieves data from a specific tender.
            """
            logger.info('_retrieve_tender_data(%d)', base_id)
            url = 'http://www.base.gov.pt/base2/rest/anuncios/%d' % base_id
            return self.goToPage(url)

        file_name = '%s/%d.dat' % (self.tenders_directory, base_id)
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            f.close()
        except IOError:
            # online retrieval
            data = _retrieve_tender_data()
            f = open(file_name, "wb")
            pickle.dump(data, f)
            f.close()
        return data

    @staticmethod
    def _save_tender(item):
        data = {'base_id': item['id'],
                'act_type': clean_act_type(item['type']),
                'model_type': clean_model_type(item['modelType']),
                'contract_type': clean_contract_type(item['contractType']),
                'description': item['contractDesignation'],
                'announcement_number': item['announcementNumber'],
                'dre_number': int(item['dreNumber']),
                'dre_series': int(item['dreSeries']),
                'dre_document': clean_dre_document(item['reference']),
                'publication_date': clean_date(item['drPublicationDate']),
                'deadline_date': clean_deadline(item['drPublicationDate'], item['proposalDeadline']),
                'cpvs': clean_cpvs(item['cpvs']),
                'price': clean_price(item['basePrice'])}

        # we try to associate the cpvs to a category
        try:
            data['category'] = models.Category.objects.get(code=data['cpvs'])
        except models.Category.DoesNotExist:
            logger.warning('Category "%s" not found', data['cpvs'])
            data['category'] = None

        # we try to see if it already exists
        try:
            tender = models.Tender.objects.get(base_id=data['base_id'])
            logger.info('_save_tender(%s): tender %d already exists', item['id'], data['base_id'])
        except models.Tender.DoesNotExist:
            # if it doesn't exist, we create it
            tender = models.Tender.objects.create(**data)
            logger.info('_save_tender(%s): tender %d saved', item['id'], data['base_id'])

        contractors = clean_entities(item['contractingEntities'])
        tender.contractors.add(*list(contractors))

    def _save_tenders(self):
        base_id = self._last_base_id() - 1000
        error_counter = 0
        while True:
            try:
                data = self._retrieve_and_cache_tender_data(base_id)
                error_counter = 0
            except (HTTPError, ValueError):
                error_counter += 1
                if error_counter == 100:
                    return base_id
                base_id += 1
                continue

            try:
                self._save_tender(data)
            # this has given errors before, we log the contract number to gain some information.
            except:
                logger.exception('error on saving tender %d', base_id)
                raise

            base_id += 1

    def update(self):
        """
        Goes to all blocks and saves all entities in each block.
        Once a block is completely empty, we stop.
        """
        self._save_tenders()


class DynamicDataCrawler():
    def __init__(self):
        self.entities_crawler = EntitiesCrawler()
        self.contracts_crawler = ContractsCrawler()
        self.tenders_crawler = TendersCrawler()

    def update_all(self):
        modified_entities = []

        modified_entities += self.entities_crawler.update()
        modified_entities += self.contracts_crawler.update()
        self.tenders_crawler.update()

        # see http://stackoverflow.com/a/7961390/931303
        def distinct(items):
            """
            Returns distinct a list of distinct elements
            """
            return list(set(items))

        return distinct(modified_entities)

crawler = DynamicDataCrawler()
