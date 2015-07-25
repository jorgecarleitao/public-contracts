import os
import shutil

import django.test

from contracts.crawler import EntitiesCrawler, ContractsCrawler, TendersCrawler


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
