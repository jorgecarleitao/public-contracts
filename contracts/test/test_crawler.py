from unittest import TestCase, skipUnless
from django.core.exceptions import ValidationError

from contracts.crawler import ContractsCrawler, TendersCrawler, DynamicCrawler, \
    JSONLoadError, ContractsStaticDataCrawler
from contracts import models

from contracts.test import CrawlerTestCase, EntitiesCrawler, HAS_REMOTE_ACCESS


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
        ContractsStaticDataCrawler().save_act_types()
        ContractsStaticDataCrawler().save_model_types()

        self.assertEqual(models.ProcedureType.objects.count(), 7)
        self.assertEqual(models.ContractType.objects.count(), 8)
        self.assertEqual(models.ActType.objects.count(), 4)
        self.assertEqual(models.ModelType.objects.count(), 9)


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

        models.ActType.objects.create(name='Anúncio de procedimento', base_id=1)
        models.ModelType.objects.create(name='Concurso público', base_id=1)
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

    def test_update(self):
        pt = models.Country.objects.create(name='Portugal')
        vs = models.District.objects.create(name='Viseu', country=pt, base_id=1)
        models.Council.objects.create(name='Viseu', district=vs, base_id=1)

        d = models.District.objects.create(name='Faro', country=pt, base_id=2)
        models.Council.objects.create(name='Faro', district=d, base_id=2)

        models.ContractType.objects.create(name='Aquisição de serviços', base_id=1)
        models.ProcedureType.objects.create(name='Ajuste directo', base_id=1)

        c = ContractsCrawler()

        c.update(7, 10)
        # test missing contracts are added
        models.Contract.objects.get(base_id=27).delete()
        mods = c.update(7, 10)
        self.assertEqual(1, mods['added'])

        # test removed contracts are added; deleted contracts are deleted
        contract = models.Contract.objects.get(base_id=27)
        contract.base_id = 28
        contract.save()
        mods = c.update(7, 10)
        self.assertEqual(1, mods['deleted'])
        self.assertEqual(1, mods['added'])

        # test modified contracts are updated
        contract = models.Contract.objects.get(base_id=27)
        contract.price = -10
        contract.save()
        mods = c.update(7, 10)
        self.assertEqual(1, mods['updated'])

    def test_update_limits(self):
        c = ContractsCrawler()

        # end<0 does nothing
        mod = c.update(2, -1)
        for x in mod:
            self.assertEqual(0, mod[x])

        # start>end does nothing
        mod = c.update(2, 1)
        for x in mod:
            self.assertEqual(0, mod[x])

        # end = None
        mod = c.update(9000000000, None)
        for x in mod:
            self.assertEqual(0, mod[x])

    def test_update_entities(self):
        c = EntitiesCrawler()
        with self.assertRaises(ValidationError):
            c.update(0, 1)

        models.Country.objects.create(name='Portugal')

        mods = c.update(0, 1)
        self.assertEqual(2, mods['added'])

    def test_update_tenders(self):
        c = TendersCrawler()
        with self.assertRaises(ValidationError):
            c.update(0, 1)

        models.Country.objects.create(name='Portugal')
        models.ModelType.objects.create(name='Concurso público', base_id=1)
        models.ActType.objects.create(name='Declaração de retificação de anúncio',
                                      base_id=1)
        models.ActType.objects.create(name='Anúncio de procedimento',
                                      base_id=2)
        models.ContractType.objects.create(name='Empreitadas de obras públicas',
                                           base_id=1)

        mods = c.update(0, 1)
        self.assertEqual(2, mods['added'])
