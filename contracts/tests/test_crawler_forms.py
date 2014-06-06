# coding=utf-8
from unittest import TestCase
from django.core.exceptions import ValidationError

from contracts.crawler_forms import PriceField, clean_place


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
