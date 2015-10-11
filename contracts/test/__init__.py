import os
import shutil

import django.test

from contracts.crawler import EntitiesCrawler, ContractsCrawler, TendersCrawler, \
    StaticDataCrawler


class CrawlerTestCase(django.test.TestCase):
    """
    Changes the directory of the crawlers to '_data' and creates the directory
    in the setUp, and erases the directory in tearDown.
    """
    @classmethod
    def setUpClass(cls):
        if os.path.exists('_data'):
            shutil.rmtree('_data')
        os.makedirs('_data')

        for klass in [EntitiesCrawler, ContractsCrawler, TendersCrawler]:
            klass.object_directory = '_data'

        super(CrawlerTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(CrawlerTestCase, cls).tearDownClass()
        shutil.rmtree('_data')

        for klass in [EntitiesCrawler, ContractsCrawler, TendersCrawler]:
            klass.object_directory = 'data'

    @staticmethod
    def create_static_fixture():
        c = StaticDataCrawler()
        c.retrieve_and_save_all()

    @staticmethod
    def add_contracts(*args):
        c = ContractsCrawler()
        for id in args:
            c.update_instance(id)

    @staticmethod
    def add_tenders(*args):
        c = TendersCrawler()
        for id in args:
            c.update_instance(id)
