from django.test import TestCase

from contracts.crawler import ContractsCrawler
from contracts.tasks import create_static_fixture


def create_fixture(*args):
    create_static_fixture()
    c = ContractsCrawler()
    for id in args:
        contract, _ = c.update_instance(id)


class TestCrawler(TestCase):

    def test_basic(self):
        create_static_fixture()

        c = ContractsCrawler()

        contract, created = c.update_instance(35356)

        self.assertEqual(35356, contract.base_id)
        self.assertEqual(None, contract.category)
