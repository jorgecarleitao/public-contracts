from unittest import TestCase, skipUnless
import datetime

from django.core.exceptions import ValidationError
import django.test

from contracts.crawler_forms import PriceField, clean_place, TimeDeltaField, \
    CPVSField, CountryChoiceField, ContractTypeField, EntitiesField
from contracts import models

from contracts.test import CrawlerTestCase, HAS_REMOTE_ACCESS


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


class CountryChoiceFieldTestCase:
    def setUp(self):
        self.field = CountryChoiceField(required=False)

    def test_none(self):
        self.assertEqual(self.field.clean('Não definido.'), None)

    def test_valid(self):
        pt = models.Country.objects.create(name='Portugal')
        de = models.Country.objects.create(name='Alemanha')

        self.assertEqual(self.field.clean('Portugal'), pt)
        self.assertEqual(self.field.clean('Alemanha'), de)

    def test_invalid(self):
        self.assertRaises(ValidationError, self.field.clean, 'Non-country')


class ContractTypeFieldTestCase(django.test.TestCase):

    @classmethod
    def setUpTestData(cls):
        models.ContractType.objects.create(base_id=1,
                                           name='Concessão de obras públicas')
        models.ContractType.objects.create(base_id=2,
                                           name='Aquisição de bens móveis')
        models.ContractType.objects.create(base_id=3,
                                           name='Outros')

        cls.field = ContractTypeField(required=False)

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


@skipUnless(HAS_REMOTE_ACCESS, 'Can\'t reach BASE')
class EntitiesFieldTestCase(CrawlerTestCase):

    def test_clean(self):
        models.Country.objects.create(name='Portugal')

        field = EntitiesField()
        with self.assertRaises(ValidationError):
            field.clean([{'id': -1}])

        field.clean([{'id': 1}])
        self.assertEqual(models.Entity.objects.count(), 1)

        models.Entity.objects.all().delete()

        # ensure correct rollback after a fail
        with self.assertRaises(ValidationError):
            field.clean([{'id': 1}, {'id': -1}])
        self.assertEqual(models.Entity.objects.count(), 0)
