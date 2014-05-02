from datetime import datetime, timedelta
import os
import pickle
import re
import mechanize as mc
import json

import models


def clean_price(item):
    """
    Transforms a string like '1.002,54 \eurochar'
    into 100254 (cents).
    """
    price = item.split(' ')[0]
    price = price.replace(".", "").replace(",", "")
    return int(price)


def clean_entities(items):
    """
    items is a list of dictionaries with key 'id'.
    We pick them all, or raise an IndexError if any of them doesn't exist (critical error).
    """
    entities = models.Entity.objects.filter(base_id__in=[item['id'] for item in items])

    # we check that all entities are there
    if entities.count() != len(items):
        raise IndexError

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
        country = models.Country.objects.get(name=item['country'])
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

    class NoMoreEntriesError:
        pass

    def __init__(self):
        # Browser
        br = mc.Browser()

        br.set_handle_robots(False)

        # User-Agent. For choosing one, use for instance this with your browser: http://whatsmyuseragent.com/
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) '
                                        'AppleWebKit/537.36 (KHTML, like Gecko)'),
                         ('Range', "items=0-24")]
        self.browser = br

    def goToPage(self, url):
        response = self.browser.open(url)
        return response.read()


class JSONCrawler(AbstractCrawler):
    """
    A crawler specific for retrieving JSON content.
    """
    def goToPage(self, url):
        return json.loads(super(JSONCrawler, self).goToPage(url))


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
    def _get_entities_block(self, block):
        """
        Returns a block of 25 entities from a file.
        If the file doesn't exist or returns less than 25 entries,
        it hits BASE's database and updates the file.

        It raises a `NoMoreEntriesError` if the retrieval returned 0 entries i.e. if have we reached
        the last existing entity in Base's database.
        """

        def _retrieve_entities():
            print '_retrieve_entities(%d)' % block
            self.browser.addheaders[1] = ('Range', "items=%d-%d" % self.block_to_range(block))
            data = self.goToPage("http://www.base.gov.pt/base2/rest/entidades")
            if len(data) == 0:
                raise self.NoMoreEntriesError
            return data

        file_name = '%s/%d_entities.dat' % (self.data_directory, block)
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            if len(data) != 25:  # if block is not complete, we retrieve it again to try to complete it.
                print '_get_entities_block(%d)' % block,
                print 'returns len(data) = %d != 25' % len(data)
                raise IOError
            f.close()
        except IOError:
            data = _retrieve_entities()
            f = open(file_name, "wb")
            pickle.dump(data, f)
            f.close()
        return data

    def _last_entity_block(self):
        """
        Returns the last block we were able to retrieve from the database.
        This is computed using the files we saved. The regex expression must be compatible to the
        name given in `_get_entities_block`.
        """
        regex = re.compile(r"(\d+)_entities.dat")
        files = [int(re.findall(regex, f)[0]) for f in os.listdir('%s/' % self.data_directory) if re.match(regex, f)]
        files = sorted(files, key=lambda x: int(x), reverse=True)
        if len(files):
            return files[0]
        else:
            return 0

    def _save_entities(self, block):
        """
        Saves a set of 25 entities, identified by a block, into the database.
        If an entity already exists, it updates its data.
        """
        print '_save_entities(%d)' % block

        created_entities = []
        for data in self._get_entities_block(block):
            country = clean_country(data)

            # if entity exists, we update its data
            try:
                entity = models.Entity.objects.get(base_id=int(data['id']))
                entity.name = data['description']
                entity.country = country
                entity.nif = data['nif']
                entity.save()
            # else, we create it with the data
            except models.Entity.DoesNotExist:
                entity = models.Entity.objects.create(name=data['description'],
                                                      base_id=int(data['id']),
                                                      country=country,
                                                      nif=data['nif'])
                created_entities.append(entity)

        return created_entities

    def update(self):
        """
        Goes to all blocks and saves all entities in each block.
        Once a retrieved block is completely empty, we stop.
        """
        created_entities = []

        block = self._last_entity_block()
        while True:
            try:
                created_entities += self._save_entities(block)
                block += 1
            except self.NoMoreEntriesError:
                break

        return created_entities


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
            self.browser.addheaders[1] = ('Range', "items=%d-%d" % self.block_to_range(block))
            data = self.goToPage("http://www.base.gov.pt/base2/rest/contratos")
            if len(data) == 0:  # if there are no entries, we just stop the procedure.
                raise self.NoMoreEntriesError
            return data

        file_name = '%s/%d.dat' % (self.data_directory, block)
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            if len(data) != 25:  # if block is not complete, we retrieve it again to complete it.
                # todo, write another error for this case
                print '_get_contracts_block(%d)' % block,
                print 'returns len(data) = %d != 25' % len(data)
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
            print '_retrieve_contract(%d)' % base_id
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

    @staticmethod
    def _save_contract(item):
        print '_save_contract(%s):' % item['id'],
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
            print 'contract %d already exists' % data['base_id']
        except models.Contract.DoesNotExist:
            # if it doesn't exist, we create it
            contract = models.Contract.objects.create(**data)
            print 'contract %d saved' % data['base_id']

        contractors = clean_entities(item['contracting'])
        contracted = clean_entities(item['contracted'])
        contract.contracted.add(*list(contracted))
        contract.contractors.add(*list(contractors))

        return list(contracted) + list(contractors)

    def _save_contracts(self, block):
        print 'save_contracts(%d)' % block
        raw_contracts = self._get_contracts_block(block)

        affected_entities = []
        for raw_contract in raw_contracts:
            try:
                data = self._retrieve_and_save_contract_data(raw_contract['id'])
                affected_entities += self._save_contract(data)
            # this has given errors before, we print the contract number to gain some information.
            except:
                print 'error on saving contract %d' % raw_contract['id']
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
            print '_retrieve_tender_data(%d)' % base_id
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
        print '_save_tender(%s):' % item['id'],
        data = {'base_id': item['id'],
                'act_type': clean_act_type(item['type']),
                'model_type': clean_model_type(item['modelType']),
                'contract_type': clean_contract_type(item[u'contractTypes']),
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
            data['category'] = None

        # we try to see if it already exists
        try:
            tender = models.Tender.objects.get(base_id=data['base_id'])
            print 'tender %d already exists' % data['base_id']
        except models.Tender.DoesNotExist:
            # if it doesn't exist, we create it
            tender = models.Tender.objects.create(**data)
            print 'tender %d saved' % data['base_id']

        contractors = clean_entities(item['contractingEntities'])
        tender.contractors.add(*list(contractors))

    def _save_tenders(self):
        base_id = self._last_base_id() - 1000
        error_counter = 0
        while True:
            try:
                data = self._retrieve_and_cache_tender_data(base_id)
                error_counter = 0
            except mc.HTTPError:
                error_counter += 1
                if error_counter == 100:
                    return base_id
                base_id += 1
                continue

            try:
                self._save_tender(data)
            # this has given errors before, we print the contract number to gain some information.
            except:
                print 'error on saving tender %d' % base_id
                #if base_id != 41407 and base_id != 41445:
                #    raise

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
