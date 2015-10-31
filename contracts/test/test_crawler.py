from unittest import TestCase, skipUnless

from contracts.crawler import ContractsCrawler, TendersCrawler, DynamicCrawler, \
    JSONLoadError, ContractsStaticDataCrawler, TendersStaticDataCrawler
from contracts import models

from contracts.test import CrawlerTestCase, HAS_REMOTE_ACCESS


@skipUnless(HAS_REMOTE_ACCESS, 'Can\'t reach BASE')
class DynamicCrawlerTestCase(TestCase):

    def setUp(self):
        self.crawler = DynamicCrawler()

    def test_raise_json_error(self):
        """
        Regression test for #17: if object doesn't exist,
        raise JSONLoadError
        """
        self.assertRaises(JSONLoadError, self.crawler.get_json,
                          'http://www.base.gov.pt/base2/rest/entidades/322')

        self.assertRaises(JSONLoadError, self.crawler.get_json,
                          'http://www.base.gov.pt/base2/rest/contratos/0')

        self.assertRaises(JSONLoadError, self.crawler.get_json,
                          'http://www.base.gov.pt/base2/rest/anuncios/0')


@skipUnless(HAS_REMOTE_ACCESS, 'Can\'t reach BASE')
class StaticDataCrawlerTestCase(TestCase):

    def test_countries_districts_counties(self):
        ContractsStaticDataCrawler().save_all_countries()
        self.assertEqual(models.Country.objects.count(), 255)

        ContractsStaticDataCrawler().save_all_districts()
        self.assertEqual(models.District.objects.count(), 23)

        faro = models.District.objects.get(name='Faro')
        ContractsStaticDataCrawler().save_councils(faro)
        self.assertEqual(models.Council.objects.count(), 16)

    def test_types(self):
        ContractsStaticDataCrawler().save_procedures_types()
        ContractsStaticDataCrawler().save_contracts_types()

        self.assertEqual(models.ProcedureType.objects.count(), 7)
        self.assertEqual(models.ContractType.objects.count(), 8)


@skipUnless(HAS_REMOTE_ACCESS, 'Can\'t reach BASE')
class TestCrawler(CrawlerTestCase):

    def test_basic(self):
        models.Country.objects.create(name='Portugal')

        models.ProcedureType.objects.create(name='Ajuste directo', base_id=1)

        c = ContractsCrawler()

        contract, _ = c.update_instance(35356)

        self.assertEqual(35356, contract.base_id)
        self.assertEqual(None, contract.category)

    def test_tenders(self):
        models.Country.objects.create(name='Portugal')
        TendersStaticDataCrawler().retrieve_and_save_all()
        models.ContractType.objects.create(name='Aquisição de bens móveis',
                                           base_id=1)

        c = TendersCrawler()

        tender, created = c.update_instance(3957)
        self.assertEqual(3957, tender.base_id)
        self.assertEqual(None, tender.category)

    def test_retrieve_twice(self):
        models.Country.objects.create(name='Portugal')

        models.ProcedureType.objects.create(name='Ajuste directo', base_id=1)

        c = ContractsCrawler()

        contract, created = c.update_instance(35356)
        self.assertTrue(created)

        contract1, created = c.update_instance(35356)
        self.assertFalse(created)

        self.assertEqual(contract, contract1)

        contract1, created = c.update_instance(35356, flush=True)
        self.assertFalse(created)

    def test_update(self):
        pt = models.Country.objects.create(name='Portugal')
        vs = models.District.objects.create(name='Viseu', country=pt, base_id=1)
        models.Council.objects.create(name='Viseu', district=vs, base_id=1)

        d = models.District.objects.create(name='Faro', country=pt, base_id=2)
        models.Council.objects.create(name='Faro', district=d, base_id=2)

        models.ContractType.objects.create(name='Aquisição de serviços', base_id=1)
        models.ProcedureType.objects.create(name='Ajuste directo', base_id=1)

        c = ContractsCrawler()

        c.update_batch(7, 10)
        # test missing contracts are added
        models.Contract.objects.get(base_id=27).delete()
        mods = c.update_batch(7, 10)
        self.assertEqual(1, mods['added'])

        # test removed contracts are added; deleted contracts are deleted
        contract = models.Contract.objects.get(base_id=27)
        contract.base_id = 28
        contract.save()
        mods = c.update_batch(7, 10)
        self.assertEqual(1, mods['deleted'])
        self.assertEqual(1, mods['added'])

        # test modified contracts are updated
        contract = models.Contract.objects.get(base_id=27)
        contract.price = -10
        contract.save()
        mods = c.update_batch(7, 10)
        self.assertEqual(1, mods['updated'])
