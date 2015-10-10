from contracts.crawler import ContractsCrawler, TendersCrawler
from contracts.test import CrawlerTestCase


class TestCrawler(CrawlerTestCase):

    def test_basic(self):
        self.create_fixture()

        c = ContractsCrawler()

        contract, created = c.update_instance(35356)

        self.assertEqual(35356, contract.base_id)
        self.assertEqual(None, contract.category)

        # test tender update
        c = TendersCrawler()

        tender, created = c.update_instance(3957)
        self.assertEqual(3957, tender.base_id)
        self.assertEqual(None, tender.category)
