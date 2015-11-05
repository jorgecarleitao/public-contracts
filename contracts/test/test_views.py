from unittest import skipUnless, skip
from urllib.request import urlopen
from datetime import datetime

from django.core.urlresolvers import reverse
import django.test
from tests import SphinxQLTestCase
from contracts.test import HAS_REMOTE_ACCESS

from contracts.views import home, contracts_list, categories_list, entities_list, \
    tenders_list
from contracts.entity_views import main_view as entity_main_view, \
    contracts as entity_contracts, costumers as entity_costumers, \
    contracts_made_time_series, contracts_received_time_series, \
    tenders as entity_tenders
from contracts.category_views import main_view as category_main_view, \
    contracts as category_contracts, contractors as category_contractors, \
    contracted as category_contracted, tenders as category_tenders
from contracts.contract_views import main_view as contract_main_view
from contracts.models import Entity, Contract, Tender, ActType, ModelType, Category


class TestBasic(django.test.TestCase):

    def setUp(self):
        super(TestBasic, self).setUp()

        c = Contract.objects.create(
            base_id=1, contract_description='da', price=100,
            added_date=datetime(year=2003, month=1, day=1),
            signing_date=datetime(year=2003, month=1, day=1))
        e1 = Entity.objects.create(name='test1', base_id=1, nif='nif')
        e2 = Entity.objects.create(name='test2', base_id=2, nif='nif')

        c.contractors.add(e1)
        c.contracted.add(e2)

        c = Contract.objects.create(
            base_id=2, contract_description='da', price=100,
            added_date=datetime(year=2008, month=1, day=1),
            signing_date=datetime(year=2008, month=1, day=1))
        c.contractors.add(e1)
        c.contracted.add(e2)

    def test_home(self):
        response = self.client.get(reverse(home))
        self.assertEqual(200, response.status_code)

    def test_contracts_list(self):
        response = self.client.get(reverse(contracts_list))
        self.assertEqual(200, response.status_code)

        contracts = response.context['contracts']
        self.assertEqual(2, len(contracts))

        # order is correct
        self.assertEqual(2, contracts[0].base_id)

    def test_contract_main_view(self):
        response = self.client.get(reverse(contract_main_view, args=(1,)))
        self.assertEqual(200, response.status_code)

    def test_categories_list(self):
        response = self.client.get(reverse(categories_list))
        self.assertEqual(200, response.status_code)

    def test_entities_list(self):
        response = self.client.get(reverse(entities_list))
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, len(response.context['entities']))

    def test_tenders_list(self):
        response = self.client.get(reverse(tenders_list))
        self.assertEqual(200, response.status_code)


class TestContractsContext(django.test.TestCase):

    def test_sorting(self):
        Contract.objects.create(base_id=1, contract_description='da',
                                price=100, added_date=datetime(year=2004, month=1,
                                                               day=1))
        Contract.objects.create(base_id=2, contract_description='da',
                                price=200, added_date=datetime(year=2003, month=1,
                                                               day=1))

        response = self.client.get(reverse(contracts_list), {'sorting': 'date'})
        contracts = response.context['contracts']

        self.assertEqual(2, len(contracts))
        self.assertEqual(1, contracts[0].base_id)

        response = self.client.get(reverse(contracts_list), {'sorting': 'price'})
        contracts = response.context['contracts']

        self.assertEqual(2, contracts[0].base_id)

    def test_range(self):
        Contract.objects.create(base_id=1, contract_description='da', price=100,
                                added_date=datetime(year=2004, month=5, day=1),
                                signing_date=datetime(year=2004, month=5, day=1))
        Contract.objects.create(base_id=2, contract_description='da', price=200,
                                added_date=datetime(year=2003, month=5, day=1),
                                signing_date=datetime(year=2003, month=5, day=1))

        # check only 2 contracts exist
        response = self.client.get(reverse(contracts_list))
        self.assertEqual(2, len(response.context['contracts']))

        response = self.client.get(reverse(contracts_list),
                                   {'range': '5/1/2004 - 5/1/2004'})
        contracts = response.context['contracts']

        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(contracts))
        self.assertEqual(1, contracts[0].base_id)

    def test_page(self):
        response = self.client.get(reverse(contracts_list), {'page': '100'})
        self.assertEqual(200, response.status_code)

    def test_wrong_range(self):
        response = self.client.get(reverse(contracts_list), {'range': '1'})

        self.assertEqual(200, response.status_code)


class TestEntityViews(django.test.TestCase):

    @skipUnless(HAS_REMOTE_ACCESS, 'Can\'t reach BASE')
    def test_base_url(self):
        entity = Entity.objects.create(name='test1', base_id=20, nif='nif')
        self.assertEqual(200, urlopen(entity.get_base_url()).getcode())

    def test_main(self):
        c = Contract.objects.create(
            base_id=1, contract_description='da', price=100,
            added_date=datetime(year=2003, month=1, day=1),
            signing_date=datetime(year=2003, month=1, day=1)
        )

        e1 = Entity.objects.create(name='test1', base_id=20, nif='nif')
        e2 = Entity.objects.create(name='test2', base_id=21, nif='nif')

        c.contractors.add(e1)
        c.contracted.add(e2)

        response = self.client.get(reverse(entity_main_view, args=(e1.base_id,)))
        self.assertEqual(200, response.status_code)
        self.assertEqual(e1.base_id, response.context['entity'].base_id)

        # check contracts view
        response = self.client.get(reverse(entity_contracts, args=(e1.base_id,)))
        self.assertEqual(200, response.status_code)
        self.assertEqual(c.base_id, response.context['contracts'][0].base_id)

        # costumers
        response = self.client.get(reverse(entity_costumers, args=(e2.base_id,)))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context['entities']))

        response = self.client.get(reverse(contracts_made_time_series,
                                           args=(e1.base_id,)))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse(contracts_received_time_series,
                                           args=(e2.base_id,)))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse(entity_tenders, args=(20,)))
        self.assertEqual(200, response.status_code)


class TestCategoryViews(django.test.TestCase):

    def test_main(self):
        cat = Category.add_root(code='45233141-9')

        act_type = ActType.objects.create(base_id=1, name='bla')
        model_type = ModelType.objects.create(base_id=1, name='bla')

        t = Tender.objects.create(
            base_id=1, publication_date=datetime(year=2003, month=1, day=1),
            deadline_date=datetime(year=2003, month=1, day=5),
            price=100, act_type=act_type, model_type=model_type,
            category=cat
        )

        c = Contract.objects.create(base_id=1, contract_description='da',
                                    price=100, added_date=datetime(year=2003,
                                                                   month=1,
                                                                   day=1),
                                    category=cat)

        e1 = Entity.objects.create(name='test1', base_id=20, nif='nif')
        e2 = Entity.objects.create(name='test2', base_id=21, nif='nif')

        c.contractors.add(e1)
        c.contracted.add(e2)

        # main view
        response = self.client.get(reverse(category_main_view, args=(cat.id,)))
        self.assertEqual(200, response.status_code)

        # contracts
        response = self.client.get(reverse(category_contracts, args=(cat.id,)))
        self.assertEqual(c.base_id, response.context['contracts'][0].base_id)

        # contractors
        response = self.client.get(reverse(category_contractors, args=(cat.id,)))
        self.assertEqual(e1.base_id, response.context['entities'][0].base_id)

        # contracted
        response = self.client.get(reverse(category_contracted, args=(cat.id,)))
        self.assertEqual(e2.base_id, response.context['entities'][0].base_id)

        # tenders
        response = self.client.get(reverse(category_tenders, args=(cat.id,)))
        self.assertEqual(t.base_id, response.context['tenders'][0].base_id)


class TestEntitiesContext(django.test.TestCase):

    def test_type(self):
        # two municipalities
        Entity.objects.create(nif='506780902', base_id=5826, name='bla')
        Entity.objects.create(nif='506572218', base_id=101, name='bla1')

        # two counties
        Entity.objects.create(nif='501335480', base_id=21, name='bla1')
        Entity.objects.create(nif='510840132', base_id=22, name='bla1')

        response = self.client.get(reverse(entities_list))
        entities = response.context['entities']
        self.assertEqual(4, len(entities))

        response = self.client.get(reverse(entities_list),
                                   {'type': 'municipality'})
        entities = response.context['entities']
        self.assertEqual(2, len(entities))

        response = self.client.get(reverse(entities_list),
                                   {'type': 'county'})
        self.assertEqual(response.status_code, 200)
        entities = response.context['entities']
        self.assertEqual(2, len(entities))

    def test_sorting(self):
        # e1 and e2 have municipalities NIFs
        e1 = Entity.objects.create(nif='506780902', base_id=5826, name='bla')
        e2 = Entity.objects.create(nif='506572218', base_id=101, name='bla1')
        e3 = Entity.objects.create(nif='dasda', base_id=21, name='bla2')
        e4 = Entity.objects.create(nif='dasda', base_id=22, name='bla2')

        c1 = Contract.objects.create(base_id=1, contract_description='da',
                                     price=200, added_date=datetime(year=2003,
                                                                    month=1,
                                                                    day=1))
        c2 = Contract.objects.create(base_id=2, contract_description='da',
                                     price=100, added_date=datetime(year=2003,
                                                                    month=1,
                                                                    day=1))

        c1.contractors.add(e1)
        c1.contracted.add(e3)
        c2.contractors.add(e2)
        c2.contracted.add(e4)

        e1.compute_data()
        e2.compute_data()
        e3.compute_data()
        e4.compute_data()

        # c1 is more expensive than c2
        response = self.client.get(reverse(entities_list), {'type': 'municipality',
                                                            'sorting': 'expenses'})
        entities = response.context['entities']
        self.assertEqual(2, len(entities))
        self.assertEqual(e1, entities[0])
        self.assertEqual(e2, entities[1])

        # the hired entities must also be ordered accordingly.
        response = self.client.get(reverse(entities_list), {'sorting': 'earnings'})
        entities = response.context['entities']
        self.assertEqual(4, len(entities))
        self.assertEqual(e3, entities[0])
        self.assertEqual(e4, entities[1])

    def test_nif_search(self):
        Entity.objects.create(nif='506780902', base_id=5826, name='bla')

        response = self.client.get(reverse(entities_list), {'search': '506780902'})

        # a redirect
        self.assertEqual(302, response.status_code)

    def test_page(self):
        response = self.client.get(reverse(entities_list), {'page': '100'})
        self.assertEqual(200, response.status_code)

    def test_wrong_get(self):
        response = self.client.get(reverse(entities_list), {'sorting': '1'})

        self.assertEqual(200, response.status_code)


class TestTendersContext(django.test.TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestTendersContext, cls).setUpTestData()

        act_type = ActType.objects.create(base_id=1, name='bla')
        model_type = ModelType.objects.create(base_id=1, name='bla')

        cls.t1 = Tender.objects.create(
            base_id=1, publication_date=datetime(year=2003, month=1, day=1),
            deadline_date=datetime(year=2003, month=1, day=5),
            price=100, act_type=act_type, model_type=model_type
        )
        cls.t2 = Tender.objects.create(
            base_id=2, publication_date=datetime(year=2004, month=1, day=1),
            deadline_date=datetime(year=2004, month=1, day=5),
            price=50, act_type=act_type, model_type=model_type
        )

    def test_sorting(self):
        response = self.client.get(reverse(tenders_list), {'sorting': 'date'})
        tenders = response.context['tenders']

        self.assertEqual(2, len(tenders))
        self.assertEqual(self.t2, tenders[0])
        self.assertEqual(self.t1, tenders[1])

        response = self.client.get(reverse(tenders_list), {'sorting': 'price'})
        tenders = response.context['tenders']

        self.assertEqual(self.t1, tenders[0])
        self.assertEqual(self.t2, tenders[1])

    def test_range(self):
        response = self.client.get(reverse(tenders_list),
                                   {'range': '1/1/2003 - 12/12/2003'})
        tenders = response.context['tenders']

        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(tenders))
        self.assertEqual(self.t1, tenders[0])

        # both contracts are in this range
        response = self.client.get(reverse(tenders_list),
                                   {'range': '1/1/2000 - 1/1/2020'})
        tenders = response.context['tenders']

        self.assertEqual(2, len(tenders))

    def test_page(self):
        response = self.client.get(reverse(tenders_list), {'page': '100'})
        self.assertEqual(200, response.status_code)

    def test_wrong_get(self):
        response = self.client.get(reverse(tenders_list), {'sorting': '1'})

        self.assertEqual(200, response.status_code)


class TestSearch(SphinxQLTestCase):

    # this test is failing; understand why
    @skip
    def test_entities(self):
        Entity.objects.create(nif='506780902', base_id=5826,
                              name='bla termo fla blu try')
        Entity.objects.create(nif='506780903', base_id=5827,
                              name='bla termos bla')

        self.index()

        response = self.client.get(reverse(entities_list), {'search': 'tra'})
        self.assertEqual(0, len(response.context['entities']))

        response = self.client.get(reverse(entities_list), {'search': 'bla'})
        self.assertEqual(2, len(response.context['entities']))

    # this test is failing; understand why
    @skip
    def test_contracts(self):
        Contract.objects.create(base_id=1, description='double pinbal',
                                price=100, added_date=datetime(year=2004, month=1,
                                                               day=1))
        Contract.objects.create(base_id=2, description='triple pinbal',
                                price=200, added_date=datetime(year=2003, month=1,
                                                               day=1))

        self.index()

        response = self.client.get(reverse(contracts_list))
        self.assertEqual(2, len(response.context['contracts']))

        response = self.client.get(reverse(contracts_list), {'search': 'pinbal'})
        self.assertEqual(2, len(response.context['contracts']))

    # this test is failing; understand why
    @skip
    def test_tenders(self):
        act_type = ActType.objects.create(base_id=1, name='bla')
        model_type = ModelType.objects.create(base_id=1, name='bla')

        Tender.objects.create(
            base_id=1, publication_date=datetime(year=2003, month=1, day=1),
            deadline_date=datetime(year=2003, month=1, day=5),
            price=100, act_type=act_type, model_type=model_type,
            description='double something'
        )
        Tender.objects.create(
            base_id=2, publication_date=datetime(year=2004, month=1, day=1),
            deadline_date=datetime(year=2004, month=1, day=5),
            price=50, act_type=act_type, model_type=model_type,
            description='half something'
        )

        self.index()

        response = self.client.get(reverse(tenders_list))
        self.assertEqual(2, len(response.context['tenders']))

        response = self.client.get(reverse(tenders_list), {'search': 'something'})
        self.assertEqual(2, len(response.context['tenders']))
