from datetime import datetime

from django.core.management import call_command
from django.test import TestCase

from contracts.models import Entity, Contract, Category


class CommandsTestCase(TestCase):

    def test_cache(self):

        cat = Category.add_root(code='45233141-9')

        e1 = Entity.objects.create(nif='506780902', base_id=5826, name='bla')
        e2 = Entity.objects.create(nif='506572218', base_id=101, name='bla1')
        e3 = Entity.objects.create(nif='dasda', base_id=21, name='bla2')
        e4 = Entity.objects.create(nif='dasda', base_id=22, name='bla2')

        c1 = Contract.objects.create(base_id=1, contract_description='da',
                                     price=200, added_date=datetime(year=2003,
                                                                    month=1,
                                                                    day=1),
                                     category=cat)
        c2 = Contract.objects.create(base_id=2, contract_description='da',
                                     price=100, added_date=datetime(year=2003,
                                                                    month=1,
                                                                    day=1),
                                     category=cat)

        c1.contractors.add(e1)
        c1.contracted.add(e3)
        c2.contractors.add(e2)
        c2.contracted.add(e4)

        call_command('cache_contracts', all=True)

        self.assertTrue(e1.data.is_updated)
