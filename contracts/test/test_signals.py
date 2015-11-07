from datetime import datetime

import django.test

from contracts.models import Contract, Entity


class InvalidateEntityDataTestCase(django.test.TestCase):

    def setUp(self):
        self.c = Contract.objects.create(
            base_id=1, contract_description='da', price=100,
            added_date=datetime(year=2003, month=1, day=1))
        self.e1 = Entity.objects.create(name='test1', base_id=1, nif='nif')
        self.e2 = Entity.objects.create(name='test2', base_id=2, nif='nif')

        self.c.contractors.add(self.e1)
        self.c.contracted.add(self.e2)

    def test_add(self):
        self.assertFalse(self.e1.data.is_updated)
        self.assertFalse(self.e2.data.is_updated)

    def test_compute_data(self):
        self.e1.compute_data()
        self.e2.compute_data()
        self.assertTrue(self.e1.data.is_updated)
        self.assertTrue(self.e2.data.is_updated)

    def test_delete(self):
        self.e1.compute_data()
        self.e2.compute_data()
        self.c.delete()

        self.e1 = Entity.objects.get(id=self.e1.id)
        self.e2 = Entity.objects.get(id=self.e2.id)

        self.assertFalse(self.e1.data.is_updated)
        self.assertFalse(self.e2.data.is_updated)
