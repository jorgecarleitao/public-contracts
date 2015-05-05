from unittest import TestCase

from contracts.crawler import DynamicCrawler, JSONLoadError, \
    ContractsStaticDataCrawler
from contracts import models


class DynamicCrawlerTestCase(TestCase):

    def setUp(self):
        self.crawler = DynamicCrawler()

    def test_raise_json_error(self):
        """
        Regression test for #17: if object doesn't exist,
        raise JSONLoadError
        """
        self.assertRaises(JSONLoadError, self.crawler.goToPage,
                          'http://www.base.gov.pt/base2/rest/entidades/322')

        self.assertRaises(JSONLoadError, self.crawler.goToPage,
                          'http://www.base.gov.pt/base2/rest/contratos/0')

        self.assertRaises(JSONLoadError, self.crawler.goToPage,
                          'http://www.base.gov.pt/base2/rest/anuncios/0')


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
