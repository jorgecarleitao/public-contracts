from django.test import TestCase

from contracts.templatetags.contracts.humanize import intword


class TestHumanize(TestCase):

    def test_intword(self):
        self.assertEqual('10.0', intword('1000'))

        self.assertEqual('10.0 thousands', intword('1000000'))

        self.assertEqual('other', intword('other'))

        self.assertEqual('0.0', intword(None))

        self.assertEqual('1000.0 trillions',
                         intword('100000000000000000'))
