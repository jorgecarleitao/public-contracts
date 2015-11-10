from django.core.management.base import BaseCommand

from contracts.crawler import ContractsCrawler, EntitiesCrawler, TendersCrawler, \
    ContractsStaticDataCrawler
from contracts.categories_crawler import build_categories

from contracts.models import Category, ProcedureType


class Command(BaseCommand):
    help = "Populates the database."

    def add_arguments(self, parser):
        parser.add_argument(
            '--contracts',
            action='store_true',
            help='Populates contracts')

        parser.add_argument(
            '--entities',
            action='store_true',
            help='Populates entities')

        parser.add_argument(
            '--tenders',
            action='store_true',
            help='Populates tenders')

        parser.add_argument(
            '--categories',
            action='store_true',
            help='Populates categories. '
                 'Typically only needs to run once with this option.')

        parser.add_argument(
            '--static',
            action='store_true',
            help='Populates db with static data. '
                 'Typically only needs to run once with this option.')

        parser.add_argument(
            '--bootstrap',
            action='store_true',
            help='Synchronizes the database from scratch. WARNING: may take days.')

    def handle(self, **options):
        if options['static']:
            if options['bootstrap'] or not ProcedureType.objects.exists():
                ContractsStaticDataCrawler().retrieve_and_save_all()

        if options['categories']:
            if options['bootstrap'] or not Category.objects.exists():
                build_categories()

        if options['entities']:
            crawler = EntitiesCrawler()
            if options['bootstrap']:
                crawler.update(0)
            else:
                crawler.update(-2000)

        if options['contracts']:
            crawler = ContractsCrawler()
            if options['bootstrap']:
                crawler.update(0)
            else:
                crawler.update(-2000)

        if options['tenders']:
            crawler = TendersCrawler()
            if options['bootstrap']:
                crawler.update(0)
            else:
                crawler.update(-2000)
