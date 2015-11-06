from unittest import skipUnless
import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from contracts.crawler_forms import PriceField, clean_place, TimeDeltaField, \
    CPVSField, CountryChoiceField, ContractTypeField, EntitiesField, TenderForm, \
    CouncilChoiceField, CategoryField
from contracts import models

from contracts.test import HAS_REMOTE_ACCESS


class PriceFieldTestCase(TestCase):

    def setUp(self):
        self.field = PriceField()

    def test_price_field(self):
        self.assertRaises(ValidationError, self.field.clean, '10€')

    def test_cents(self):
        self.assertEqual(self.field.clean('10,34 €'), 1034)

    def test_with_period(self):
        self.assertEqual(self.field.clean('1.000,00 €'), 100000)

    def test_double_period(self):
        self.assertEqual(self.field.clean('1.000.234,00 €'), 100023400)


class CleanPlaceTestCase(TestCase):

    def test_more_than_one(self):
        value = clean_place('Portugal, Porto, Maia<BR/>'
                            'Portugal<BR/>Portugal, Distrito não determinado, '
                            'Concelho não determinado<BR/>'
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

    def test_fail(self):
        with self.assertRaises(ValidationError):
            self.field.clean('2 meses.')


class CPVSFieldTestCase(TestCase):
    def setUp(self):
        self.field = CPVSField(required=False)

    def test_correct(self):
        self.assertEqual(self.field.clean('45233141-9, Manutenção de estradas'),
                         '45233141-9')

    def test_incorrect(self):
        self.assertRaises(ValidationError, self.field.clean,
                          '4523314-9, Manutenção de estradas')

    def test_none(self):
        self.assertEqual(self.field.clean(''), None)


class CategoryFieldTestCase(TestCase):

    def test_undefined(self):
        self.assertEqual(None,
                         CategoryField(required=False).clean('Não definido.'))

        # not in our db -> `None`
        self.assertEqual(None, CategoryField(required=False).clean('45233141-9'))

    def test_valid(self):
        c = models.Category.add_root(code='45233141-9')

        self.assertEqual(c, CategoryField().clean('45233141-9'))


class CountryChoiceFieldTestCase(TestCase):
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


class CouncilChoiceFieldTestCase(TestCase):
    def setUp(self):
        self.field = CouncilChoiceField(required=False)

    def test_none(self):
        self.assertEqual(self.field.clean({'council': None}), None)

    def test_valid(self):
        pt = models.Country.objects.create(name='Portugal')
        d = models.District.objects.create(name='Viseu', country=pt, base_id=1)
        c = models.Council.objects.create(name='Viseu', district=d, base_id=1)

        value = {'council': 'Viseu', 'country': pt, 'district': d.name}
        self.assertEqual(self.field.clean(value), c)


class TenderFormTestCase(TestCase):
    def test_date_from_url(self):
        date = datetime.date(year=2010, month=8, day=12)

        # by default use publication date
        data = {'publication_date': date,
                'dre_url': 'http://dre.pt/util/getpdf.asp?s=udrcp&serie=2&'
                           'data=2009-08-12&iddr=155&iddip=402188583'}
        self.assertEqual(TenderForm.prepare_publication_date(data), date)

        # no pub_date -> fall back to url date
        data = {'publication_date': None,
                'dre_url': 'http://dre.pt/util/getpdf.asp?s=udrcp&serie=2&'
                           'data=2009-08-12'
                           '&iddr=155&iddip=402188583'}

        self.assertEqual(TenderForm.prepare_publication_date(data),
                         datetime.date(year=2009, month=8, day=12))

        # no dates -> None
        data = {'publication_date': None,
                'dre_url': 'http://dre.pt/util/getpdf.asp?s=udrcp&serie=2&'
                           'iddr=155&iddip=402188583'}
        self.assertEqual(TenderForm.prepare_publication_date(data), None)

    def test_deadline(self):
        form = TenderForm()

        date = datetime.date(year=2010, month=8, day=12)
        timedelta = datetime.timedelta(days=10)
        form.cleaned_data = {
            'publication_date': date,
            'deadline_date': timedelta}

        self.assertEqual(date + timedelta, form.clean_deadline_date())

        # should not raise ValidationError because other clean will do it.
        form.cleaned_data = {'deadline_date': timedelta}
        form.clean_deadline_date()


class ContractTypeFieldTestCase(TestCase):

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
                         models.ContractType.objects.get(
                             name='Concessão de obras públicas'))

    def test_more_than_one(self):
        self.assertEqual(
            self.field.clean('Concessão de obras públicas<br/>'
                             'Aquisição de bens móveis'),
            models.ContractType.objects.get(name='Concessão de obras públicas'))

        self.assertEqual(
            self.field.clean('Aquisição de bens móveis<br/>'
                             'Concessão de obras públicas'),
            models.ContractType.objects.get(name='Aquisição de bens móveis'))

        self.assertEqual(
            self.field.clean('Aquisição de bens móveis; '
                             'Concessão de obras públicas'),
            models.ContractType.objects.get(name='Aquisição de bens móveis'))

    def test_others(self):
        self.assertEqual(
            self.field.clean('Outros Tipos (Concessão de exploração de bens do '
                             'domínio público)'),
            models.ContractType.objects.get(name='Outros'))


@skipUnless(HAS_REMOTE_ACCESS, 'Can\'t reach BASE')
class EntitiesFieldTestCase(TestCase):

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
