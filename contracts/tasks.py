from time import sleep
from celery import shared_task
from celery.utils.log import get_task_logger

from contracts.crawler import DynamicDataCrawler, StaticDataCrawler
from contracts import models
from contracts.analysis import analysis_manager

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def create_static_fixture():
    # check if we need to download static data
    if not models.ProcedureType.objects.exists():
        c = StaticDataCrawler()
        c.retrieve_and_save_all()


@shared_task(ignore_result=True)
def create_categories_fixture():
    # check if we need to create categories
    if not models.Category.objects.exists():
        from contracts.tools.cpvs import build_categories
        build_categories()


@shared_task(ignore_result=True)
def create_fixture():
    create_static_fixture.delay()
    create_categories_fixture.delay()


@shared_task(ignore_result=True)
def retrieve_new_contracts():
    crawler = DynamicDataCrawler()
    crawler.update_all()


@shared_task(ignore_result=True)
def recompute_entities_data():
    for entity in models.Entity.objects.all():
        entity.compute_data()


@shared_task(ignore_result=True)
def recompute_categories_data():
    for category in models.Category.objects.all():
        category.compute_data()


@shared_task(ignore_result=True)
def recompute_analysis():
    for analysis in list(analysis_manager.values()):
        analysis.update()


@shared_task(ignore_result=True)
def update():
    sleep(2)
    #logger.info('Updating contracts')
    #chain = create_static_fixture.s() | create_fixture.s()
    #chain()
