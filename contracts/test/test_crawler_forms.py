# coding=utf-8
from unittest import TestCase
import datetime

from django.core.exceptions import ValidationError

from . import CrawlerTestCase
from contracts.crawler import ContractsStaticDataCrawler
from contracts.crawler_forms import PriceField, clean_place, TimeDeltaField, CPVSField, \
    CountryChoiceField, ContractTypeField, EntitiesField
from contracts import models


class PriceFieldTestCase(TestCase):

    def setUp(self):
        self.field = PriceField()

    def test_price_field(self):
        self.assertRaises(ValidationError, self.field.clean, '10€')

    def test_cents(self):
        self.assertEqual(self.field.clean('10,34 €'), 1034)

    def test_without_period(self):
        self.assertEqual(self.field.clean('10,00 €'), 1000)

    def test_with_period(self):
        self.assertEqual(self.field.clean('1.000,00 €'), 100000)

    def test_double_period(self):
        self.assertEqual(self.field.clean('1.000.234,00 €'), 100023400)


class CleanPlaceTestCase(TestCase):

    def test_more_than_one(self):
        value = clean_place('Portugal, Porto, Maia<BR/>'
                            'Portugal<BR/>Portugal, Distrito não determinado, Concelho não determinado<BR/>'
                            'Portugal, Vila Real, Vila Real')
        self.assertEqual(value, ('Portugal', 'Porto', 'Maia'))

    def test_incomplete(self):
        value = clean_place('Portugal, Porto')
        self.assertEqual(value, ('Portugal', 'Porto', None))

    def test_incomplete_more(self):
        value = clean_place('Portugal, Porto<BR/>Portugal')
        self.assertEqual(value, ('Portugal', 'Porto', None))


class TimeDeltaFieldTestCase(TestCase):

    def setUp(self):
        self.field = TimeDeltaField()

    def test_clean(self):
        self.assertEqual(self.field.clean('10 dias.'), datetime.timedelta(days=10))

    def test_zero(self):
        self.assertEqual(self.field.clean('0 dias.'), datetime.timedelta(days=0))


class CPVSFieldTestCase(TestCase):
    def setUp(self):
        self.field = CPVSField(required=False)

    def test_correct(self):
        self.assertEqual(self.field.clean('45233141-9, Manutenção de estradas'), '45233141-9')

    def test_incorrect(self):
        self.assertRaises(ValidationError, self.field.clean, '4523314-9, Manutenção de estradas')

    def test_none(self):
        self.assertEqual(self.field.clean(''), None)


class CountryChoiceFieldTestCase(TestCase):
    def setUp(self):
        crawler = ContractsStaticDataCrawler()
        crawler.save_all_countries()

        self.field = CountryChoiceField(required=False)

    def test_none(self):
        self.assertEqual(self.field.clean('Não definido.'), None)

    def test_valid(self):
        self.assertEqual(self.field.clean('Portugal'), models.Country.objects.get(name='Portugal'))
        self.assertEqual(self.field.clean('Alemanha'), models.Country.objects.get(name='Alemanha'))

    def test_invalid(self):
        self.assertRaises(ValidationError, self.field.clean, 'Non-country')


class ContractTypeFieldTestCase(TestCase):
    def setUp(self):
        crawler = ContractsStaticDataCrawler()
        crawler.save_contracts_types()

        self.field = ContractTypeField(required=False)

    def test_none(self):
        self.assertEqual(self.field.clean('Não definido.'), None)

    def test_one(self):
        self.assertEqual(self.field.clean('Concessão de obras públicas'),
                         models.ContractType.objects.get(name='Concessão de obras públicas'))

    def test_more_than_one(self):
        self.assertEqual(self.field.clean('Concessão de obras públicas<br/>Aquisição de bens móveis'),
                         models.ContractType.objects.get(name='Concessão de obras públicas'))

        self.assertEqual(self.field.clean('Aquisição de bens móveis<br/>Concessão de obras públicas'),
                         models.ContractType.objects.get(name='Aquisição de bens móveis'))

        self.assertEqual(self.field.clean('Aquisição de bens móveis; Concessão de obras públicas'),
                         models.ContractType.objects.get(name='Aquisição de bens móveis'))

    def test_others(self):
        self.assertEqual(self.field.clean('Outros Tipos (Concessão de exploração de bens do domínio público)'),
                         models.ContractType.objects.get(name='Outros'))


class EntitiesFieldTestCase(CrawlerTestCase):

    def test_clean(self):
        ContractsStaticDataCrawler().save_all_countries()

        field = EntitiesField()
        self.assertRaises(ValidationError, field.clean, [{'id': -1}])

        field.clean([{'id': 1}])
        self.assertEqual(models.Entity.objects.count(), 1)

        models.Entity.objects.all().delete()

        # ensure correct rollback after a fail
        self.assertRaises(ValidationError, field.clean, [{'id': 1}, {'id': -1}])
        self.assertEqual(models.Entity.objects.count(), 0)
