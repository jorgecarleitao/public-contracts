import urllib.request

from django.core.urlresolvers import reverse

from contracts.views import home, contracts_list, categories_list, entities_list, \
    tenders_list
from contracts.entity_views import main_view as entity_main_view, \
    contracts as entity_contracts, costumers as entity_constumers, \
    contracts_made_time_series, contracts_received_time_series, \
    tenders as entity_tenders
from contracts.contract_views import main_view as contract_main_view

from contracts.test import CrawlerTestCase


class TestBasic(CrawlerTestCase):
    def test_home(self):
        response = self.client.get(reverse(home))
        self.assertEqual(200, response.status_code)

    def test_contracts_list(self):
        self.create_fixture(35356)

        response = self.client.get(reverse(contracts_list))
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(response.context['contracts']))

        response = self.client.get(reverse(contract_main_view, args=(35356,)))
        self.assertEqual(200, response.status_code)

    def test_categories_list(self):
        response = self.client.get(reverse(categories_list))
        self.assertEqual(200, response.status_code)

    def test_entities_list(self):
        self.create_fixture(35356)

        response = self.client.get(reverse(entities_list))
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, len(response.context['entities']))

    def test_tenders_list(self):
        response = self.client.get(reverse(tenders_list))
        self.assertEqual(200, response.status_code)


class TestContractsContext(CrawlerTestCase):

    def test_sorting(self):
        self.create_fixture(35356, 2048)

        response = self.client.get(reverse(contracts_list), {'sorting': 'date'})
        contracts = response.context['contracts']

        self.assertEqual(2, len(contracts))
        self.assertEqual(35356, contracts[0].base_id)

        response = self.client.get(reverse(contracts_list), {'sorting': 'price'})
        contracts = response.context['contracts']

        self.assertEqual(2048, contracts[0].base_id)

    def test_range(self):
        # only the contract 1656582 is on 10/9/2015
        self.create_fixture(1656582, 1656371)

        response = self.client.get(reverse(contracts_list), {'range': '10/9/2015 - 10/9/2015'})
        contracts = response.context['contracts']

        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(contracts))
        self.assertEqual(1656582, contracts[0].base_id)

    def test_page(self):
        response = self.client.get(reverse(contracts_list), {'page': '100'})
        self.assertEqual(200, response.status_code)


class TestEntityViews(CrawlerTestCase):

    def test_main(self):
        # contract 1656582 contains entity 11253
        self.create_fixture(1656582)
        response = self.client.get(reverse(entity_main_view, args=(11253,)))
        self.assertEqual(200, response.status_code)

        # retrieve the entity and confirm its base_id and url are correct
        entity = response.context['entity']
        self.assertEqual(11253, entity.base_id)
        self.assertEqual(200, urllib.request.urlopen(entity.get_base_url()).getcode())

        # check contracts view
        response = self.client.get(reverse(entity_contracts, args=(entity.base_id,)))
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(response.context['contracts']))

        # costumers requires updating redundant data
        entity.compute_data()

        response = self.client.get(reverse(entity_constumers, args=(entity.base_id,)))
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(response.context['entities']))

        # the entity that hired is 83983
        response = self.client.get(reverse(contracts_made_time_series, args=(83983,)))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse(contracts_received_time_series, args=(entity.base_id,)))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse(entity_tenders, args=(entity.base_id,)))
        self.assertEqual(200, response.status_code)


class TestEntitiesContext(CrawlerTestCase):

    def test_type(self):
        # 5826 and 101 are municipalities
        # contract 1657030 is made by 5826, 1656371 is made by 101
        self.create_fixture(1657030, 1656371)
        response = self.client.get(reverse(entities_list))
        entities = response.context['entities']
        self.assertEqual(4, len(entities))
        for entity in entities:
            entity.compute_data()

        response = self.client.get(reverse(entities_list), {'type': 'municipality'})
        entities = response.context['entities']
        self.assertEqual(2, len(entities))

        # 1657030 is more expensive than 1656371
        response = self.client.get(reverse(entities_list), {'type': 'municipality',
                                                            'sorting': 'expenses'})
        entities = response.context['entities']
        self.assertEqual(2, len(entities))
        self.assertEqual(5826, entities[0].base_id)
        self.assertEqual(101, entities[1].base_id)

        # the hired entities must also be ordered accordingly.
        response = self.client.get(reverse(entities_list), {'sorting': 'earnings'})
        entities = response.context['entities']
        self.assertEqual(4, len(entities))
        self.assertEqual(15295, entities[0].base_id)
        self.assertEqual(873178, entities[1].base_id)

    def test_page(self):
        response = self.client.get(reverse(entities_list), {'page': '100'})
        self.assertEqual(200, response.status_code)
