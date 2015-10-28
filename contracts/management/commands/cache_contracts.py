from django.core.management.base import BaseCommand

from contracts.analysis import analysis_manager
from contracts.models import Entity, Category


class Command(BaseCommand):
    help = 'Computes and stores intermediary results (analysis, etc.).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Equivalent to add all options below.')

        parser.add_argument(
            '--entities',
            action='store_true',
            help='Recompute cache of entities.')

        parser.add_argument(
            '--categories',
            action='store_true',
            help='Recompute cache of categories.')

        parser.add_argument(
            '--analysis',
            action='store_true',
            help='Recompute cache of analysis.')

    def handle(self, **options):
        if options['entities'] or options['all']:
            for entity in Entity.objects.all():
                entity.compute_data()

        if options['categories'] or options['all']:
            for category in Category.objects.all():
                category.compute_data()

        if options['analysis'] or options['all']:
            for analysis in list(analysis_manager.values()):
                analysis.update()
