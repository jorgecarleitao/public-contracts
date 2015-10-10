import os
import shutil

import django.test

from contracts.crawler import EntitiesCrawler, ContractsCrawler, TendersCrawler, \
    StaticDataCrawler


class CrawlerTestCase(django.test.TransactionTestCase):
    """
    Changes the directory of the crawlers to '_data' and creates the directory
    in the setUp, and erases the directory in tearDown.
    """
    def setUp(self):
        if os.path.exists('_data'):
            shutil.rmtree('_data')
        os.makedirs('_data')

        for klass in [EntitiesCrawler, ContractsCrawler, TendersCrawler]:
            klass.object_directory = '_data'

    def tearDown(self):
        shutil.rmtree('_data')

    @staticmethod
    def create_fixture(*args):
        c = StaticDataCrawler()
        c.retrieve_and_save_all()
        c = ContractsCrawler()
        for id in args:
            contract, _ = c.update_instance(id)
