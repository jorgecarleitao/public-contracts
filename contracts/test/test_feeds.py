from datetime import datetime
from xml.dom import minidom

from django.core.urlresolvers import reverse
from django.test import TestCase

from contracts.models import Contract, Entity, ActType, ModelType, Tender, Category


class FeedTestCase(TestCase):

    def get_channel(self, response):
        doc = minidom.parseString(response.content)
        feed_elem = doc.getElementsByTagName('rss')
        feed = feed_elem[0]
        chan_elem = feed.getElementsByTagName('channel')
        return chan_elem[0]

    def assertChildNodes(self, elem, expected):
        actual = set(n.nodeName for n in elem.childNodes)
        expected = set(expected)
        self.assertEqual(actual, expected)

    def assertChildNodeContent(self, elem, expected):
        for k, v in expected.items():
            self.assertEqual(
                elem.getElementsByTagName(k)[0].firstChild.wholeText, v)


class TestContractsFeeds(FeedTestCase):

    def setUp(self):
        self.cat = Category.add_root(code='45233141-9', description_pt='cat1')

        c = Contract.objects.create(
            base_id=1, contract_description='da', price=100,
            added_date=datetime(year=2004, month=1, day=1),
            signing_date=datetime(year=2004, month=1, day=1),
            category=self.cat)

        e1 = Entity.objects.create(name='test1', base_id=20, nif='nif')
        e2 = Entity.objects.create(name='test2', base_id=21, nif='nif')

        c.contractors.add(e1)
        c.contracted.add(e2)

    def test_list(self):
        response = self.client.get(reverse('contracts_list_feed'))
        self.assertEqual(200, response.status_code)

        chan = self.get_channel(response)

        self.assertChildNodeContent(chan, {
            'title': 'Contracts in Públicos',
            'description': 'Latest contracts in Públicos',
            'link': 'http://testserver/contracts/rss',
            'language': 'en',
        })

        items = chan.getElementsByTagName('item')

        self.assertChildNodeContent(items[0], {
            'title': '1.0€ - da',
            'description': 'Contractors: test1',
            'link': 'http://testserver/contract/id1',
        })

    def test_entity_contracts(self):
        response = self.client.get(reverse('entity_contracts', args=(20,))+'/rss')
        self.assertEqual(200, response.status_code)

        chan = self.get_channel(response)

        self.assertChildNodeContent(chan, {
            'title': 'Públicos - test1',
            'description': 'Contracts with "test1"',
            'link': 'http://testserver/entity/id20/test1',
            'language': 'en',
        })

    def test_category_contracts(self):
        response = self.client.get(reverse('category_contracts_rss',
                                           args=(self.cat.id,)))
        self.assertEqual(200, response.status_code)

        chan = self.get_channel(response)

        self.assertChildNodeContent(chan, {
            'title': 'Públicos - cat1',
            'description': 'Contracts in "cat1"',
            'link': 'http://testserver/category/%d' % self.cat.id,
            'language': 'en',
        })


class TestTendersFeeds(FeedTestCase):

    def setUp(self):
        self.cat = Category.add_root(code='45233141-9', description_pt='cat1')

        act_type = ActType.objects.create(base_id=1, name='bla')
        model_type = ModelType.objects.create(base_id=1, name='bla')

        t = Tender.objects.create(
            base_id=1, publication_date=datetime(year=2003, month=1, day=1),
            deadline_date=datetime(year=2003, month=1, day=5),
            price=100, act_type=act_type, model_type=model_type,
            description='test',
            dre_url='http://www.example.com',
            category=self.cat
        )

        e1 = Entity.objects.create(name='test1', base_id=20, nif='nif')

        t.contractors.add(e1)

    def test_list(self):
        response = self.client.get(reverse('tenders_list_feed'))
        self.assertEqual(200, response.status_code)

        chan = self.get_channel(response)

        self.assertChildNodeContent(chan, {
            'title': 'Tenders in Públicos',
            'description': 'Latest tenders in Públicos',
            'link': 'http://testserver/tenders/rss',
            'language': 'en',
        })

        items = chan.getElementsByTagName('item')

        self.assertChildNodeContent(items[0], {
            'title': '1.0€ - DEADLINE: 2003-01-05 - test',
            'description': 'Contractors: test1',
            'link': 'http://www.example.com',
        })

    def test_entity_tenders(self):
        response = self.client.get(reverse('entity_tenders', args=(20,))+'/rss')
        self.assertEqual(200, response.status_code)

        chan = self.get_channel(response)

        self.assertChildNodeContent(chan, {
            'title': 'Públicos - test1',
            'description': 'Tenders created by "test1"',
            'link': 'http://testserver/entity/id20/test1',
            'language': 'en',
        })

        items = chan.getElementsByTagName('item')

        self.assertChildNodeContent(items[0], {
            'title': '1.0€ - DEADLINE: 2003-01-05 - test',
            'description': 'Contractors: test1',
            'link': 'http://www.example.com',
        })

    def test_category_tenders(self):
        response = self.client.get(reverse('category_tenders_rss',
                                           args=(self.cat.id,)))
        self.assertEqual(200, response.status_code)

        chan = self.get_channel(response)

        self.assertChildNodeContent(chan, {
            'title': 'Públicos - cat1',
            'description': 'Tenders in "cat1"',
            'link': 'http://testserver/category/%d' % self.cat.id,
            'language': 'en',
        })
